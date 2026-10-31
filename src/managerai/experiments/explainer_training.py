"""LoRA real em tarefa sintética de explicação restrita; sem rótulos esportivos.

Artefatos são experimentais. Nenhuma promoção automática nem download implícito.
O modelo base deve ser provisionado separadamente, com revisão/hash/licença.
"""
import argparse
from dataclasses import asdict
import importlib.metadata
import json
from pathlib import Path
import random
import resource
import time

from ..explanation import canonical, fingerprint, messages, validate_selection
from .artifacts import new_run_dir
from .paths import execution_code_hashes


MODEL_ID = "HuggingFaceTB/SmolLM2-135M-Instruct"
MODEL_REVISION = "12fd25f77366fa6b3b4b768ec3050bf629380bac"


def synthetic_cases(seed=42):
    """Partição por caso antes de qualquer transformação; sem dados StatsBomb.

    Supervisão gerada por template, não revisão humana. Não é dataset tático.
    """
    rng = random.Random(seed)
    cases = []
    for i in range(160):
        partition = "train" if i < 96 else "validation" if i < 120 else "test"
        n = rng.choice((0, 1, 3, 5, 7, 10))
        shots = rng.randrange(0, 30)
        cid = f"synthetic-case-{i:03d}"
        claims = [{"id": f"scope_{i}", "text": "Análise histórica, sem eficácia tática validada.", "evidence_ids": ["scope"]},
                  {"id": f"sample_{i}", "text": f"Equipe fictícia {i}: amostra de {n} jogos.", "evidence_ids": ["sample"]}]
        if n >= 5:
            claims += [{"id": f"metric_{i}", "text": f"Finalizações registradas: {shots} por jogo na amostra sintética.",
                        "evidence_ids": ["shots"]}]
        else:
            claims += [{"id": f"abstain_{i}", "text": "Amostra insuficiente; não emitir plano comparativo.", "evidence_ids": ["sufficiency"]}]
        if i % 3 == 0:
            claims += [{"id": f"roster_{i}", "text": "Elenco atual desconhecido; nenhuma sugestão individual.", "evidence_ids": ["roster"]}]
        projection = {"report_id": fingerprint(cid), "claims": claims}
        cases.append({"case_id": cid, "partition": partition, "origin": "synthetic_template_verbalization",
                      "human_reviewed": False, "insufficient": n < 5, "projection": projection,
                      "target": canonical({"claim_ids": [c["id"] for c in claims]})})
    validate_cases(cases)
    return cases


def validate_cases(cases):
    ids, contents = set(), set()
    for c in cases:
        if c["case_id"] in ids or c["partition"] not in ("train", "validation", "test"):
            raise ValueError("Caso duplicado ou partição inválida.")
        signature = fingerprint(c["projection"])
        if signature in contents:
            raise ValueError("Conteúdo duplicado entre casos.")
        ids.add(c["case_id"])
        contents.add(signature)
        validate_selection(c["target"], c["projection"])


class LocalTransformerProvider:
    provider_id = "transformers_local_experimental"

    def __init__(self, model_path, *, adapter_path=None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        torch.set_num_threads(4)
        self.model = MODEL_ID + (":lora" if adapter_path else ":base")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.network = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True,
                                                           torch_dtype=torch.float32)
        if adapter_path:
            from peft import PeftModel
            self.network = PeftModel.from_pretrained(self.network, adapter_path, local_files_only=True)
        self.network.eval()

    def generate(self, projection):
        import torch
        prompt = self.tokenizer.apply_chat_template(messages(projection), tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if inputs.input_ids.shape[1] > 700:
            raise ValueError("Projeção excede o contexto experimental.")
        with torch.no_grad():
            outputs = self.network.generate(**inputs, max_new_tokens=128, do_sample=False,
                                            max_time=45, pad_token_id=self.tokenizer.eos_token_id)
        return self.tokenizer.decode(outputs[0, inputs.input_ids.shape[1]:], skip_special_tokens=True)


def evaluate(provider, cases):
    results, started = [], time.monotonic()
    for case in cases:
        tick = time.monotonic()
        try:
            raw = provider.generate(case["projection"])
            try:
                validate_selection(raw, case["projection"])
                valid = True
            except (ValueError, TypeError, KeyError):
                valid = False
            failure = None if valid else "invalid_or_incomplete_selection"
        except Exception as exc:
            raw, valid, failure = None, False, type(exc).__name__
        results.append({"case_id": case["case_id"], "valid": valid, "raw": raw, "failure": failure,
                        "insufficient": case["insufficient"], "seconds": time.monotonic()-tick})
    n = len(results)
    insufficient = [r for r in results if r["insufficient"]]
    return {"n": n, "exact_validity_and_coverage": sum(r["valid"] for r in results)/n,
            "abstention_compliance": sum(r["valid"] for r in insufficient)/len(insufficient) if insufficient else None,
            "unsafe_content_exposed_after_validation": 0,
            "human_clarity_or_utility_reviews": 0, "duration_seconds": time.monotonic()-started,
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "cases": results}


def train(model_path, protocol_path, output_dir):
    import torch
    from peft import LoraConfig, get_peft_model
    protocol_bytes = Path(protocol_path).read_bytes()
    protocol = json.loads(protocol_bytes)
    config = protocol["explanation"]
    settings = config["training"]
    out, base = Path(output_dir).resolve(), Path(model_path).resolve()
    if out.exists() or out == base or base in out.parents:
        raise ValueError("Destino do ajuste deve ser novo e separado do modelo base.")
    provision = json.loads((base/"provision.json").read_text())
    if provision["revision"] != MODEL_REVISION or provision["license"] != "apache-2.0":
        raise ValueError("Modelo base sem proveniência aprovada.")
    from hashlib import sha256
    for name, digest in provision["sha256"].items():
        if sha256((base/name).read_bytes()).hexdigest() != digest:
            raise ValueError("Hash do modelo/tokenizador divergente.")
    out = new_run_dir(out)
    cases = synthetic_cases(config["seed"])
    (out/"dataset.json").write_text(canonical(cases), encoding="utf-8")
    manifest = {"protocol_fingerprint": fingerprint(protocol), "protocol": protocol, "code_sha256": execution_code_hashes(),
                "model": MODEL_ID, "revision": MODEL_REVISION, "base_provision": provision,
                "dataset_fingerprint": fingerprint(cases), "partitions": {
                    part: [c["case_id"] for c in cases if c["partition"] == part] for part in ("train", "validation", "test")},
                "dependencies": {p: importlib.metadata.version(p) for p in ("torch", "transformers", "peft", "tokenizers")},
                "task": config["task"], "supervision": config["supervision"], "human_reviews": 0}
    (out/"manifest.json").write_text(canonical(manifest), encoding="utf-8")
    torch.manual_seed(config["seed"])
    random.seed(config["seed"])
    torch.use_deterministic_algorithms(True)
    provider = LocalTransformerProvider(base)
    # Validação é diagnóstica; não é usada para escolher épocas ou ajustar parâmetros.
    heldout = [c for c in cases if c["partition"] == "test"]
    base_scores = evaluate(provider, heldout)
    (out/"base_evaluation.json").write_text(canonical(base_scores), encoding="utf-8")
    net = get_peft_model(provider.network, LoraConfig(r=settings["lora_rank"], lora_alpha=settings["lora_alpha"],
                         lora_dropout=0.0, target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM"))
    net.config.use_cache = False
    optimizer = torch.optim.AdamW([p for p in net.parameters() if p.requires_grad], lr=settings["learning_rate"])
    samples = []
    for c in cases:
        if c["partition"] != "train":
            continue
        prompt = provider.tokenizer.apply_chat_template(messages(c["projection"]), tokenize=False, add_generation_prompt=True)
        prefix = provider.tokenizer(prompt, add_special_tokens=False)["input_ids"]
        suffix = provider.tokenizer(c["target"] + provider.tokenizer.eos_token, add_special_tokens=False)["input_ids"]
        if len(prefix)+len(suffix) > settings["max_tokens"]:
            raise ValueError("Caso excede limite; não truncar evidência silenciosamente.")
        samples.append((prefix, suffix))
    net.train()
    losses, started = [], time.monotonic()
    for epoch in range(settings["epochs"]):
        order = list(range(len(samples)))
        random.Random(config["seed"]+epoch).shuffle(order)
        for index in order:
            prefix, suffix = samples[index]
            tokens = torch.tensor([prefix+suffix], dtype=torch.long)
            labels = torch.tensor([[-100]*len(prefix)+suffix], dtype=torch.long)
            optimizer.zero_grad(set_to_none=True)
            loss = net(input_ids=tokens, attention_mask=torch.ones_like(tokens), labels=labels).loss
            if not torch.isfinite(loss):
                raise ValueError("Loss não finita.")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
            optimizer.step()
            losses.append(float(loss.detach()))
            if len(losses) % 24 == 0:
                print(canonical({"step": len(losses), "loss": losses[-1], "seconds": time.monotonic()-started}), flush=True)
    adapter = out/"adapter"
    net.save_pretrained(adapter, safe_serialization=True)
    provider.tokenizer.save_pretrained(adapter)
    provider.network = net
    net.eval()
    net.config.use_cache = True
    tuned_scores = evaluate(provider, heldout)
    validation_scores = evaluate(provider, [c for c in cases if c["partition"] == "validation"])
    # Carregamento do artefato salvo é exercitado separadamente, sem depender de memória de treino.
    reloaded = LocalTransformerProvider(base, adapter_path=adapter)
    reload_output = reloaded.generate(heldout[0]["projection"])
    result = {"manifest_fingerprint": fingerprint(manifest), "training": {"steps": len(losses), "losses": losses,
              "duration_seconds": time.monotonic()-started,
              "trainable_parameters": sum(p.numel() for p in net.parameters() if p.requires_grad)},
              "base": base_scores, "fine_tuned": tuned_scores, "validation": validation_scores,
              "template": {"n": len(heldout), "exact_validity_and_coverage": 1.0,
                           "note": "Referência determinística; targets sintéticos são produzidos pelo mesmo template."},
              "reload_output": reload_output, "promoted": False,
              "decision": "Experimental: supervisão sintética, sem revisão humana; não comprova benefício esportivo nem requisito acadêmico.",
              "artifacts_sha256": {str(p.relative_to(out)): sha256(p.read_bytes()).hexdigest()
                                   for p in adapter.rglob("*") if p.is_file()}}
    (out/"evaluation.json").write_text(canonical(result), encoding="utf-8")
    return {"steps": len(losses), "base_valid": base_scores["exact_validity_and_coverage"],
            "tuned_valid": tuned_scores["exact_validity_and_coverage"], "promoted": False}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model-path", required=True)
    p.add_argument("--protocol", required=True)
    p.add_argument("--output-dir", required=True)
    args = p.parse_args()
    print(canonical(train(args.model_path, args.protocol, args.output_dir)))
