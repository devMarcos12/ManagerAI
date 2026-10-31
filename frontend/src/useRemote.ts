import { useEffect, useRef, useState } from 'react';

// Abort + guarda de identidade: até um fetch que ignore o cancelamento não pode
// publicar dados de uma seleção antiga. Nunca reutilizar dados de outra chave.
export function useRemote<T>(key: string | null, fetcher: (signal: AbortSignal) => Promise<T>) {
  const loader = useRef(fetcher);
  loader.current = fetcher;
  const [state, setState] = useState<{ key: string | null; data?: T; error?: unknown; loading: boolean }>({ key: null, loading: false });
  useEffect(() => {
    if (key === null) return;
    let current = true;
    const controller = new AbortController();
    setState({ key, loading: true });
    loader.current(controller.signal).then(data => { if (current) setState({ key, data, loading: false }); },
      error => { if (current) setState({ key, error, loading: false }); });
    return () => { current = false; controller.abort(); };
  }, [key]);
  return state.key === key && key !== null ? state : { key, data: undefined, error: undefined, loading: key !== null };
}

export function useDebounced<T>(value: T, delay = 250): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => { const timer = setTimeout(() => setDebounced(value), delay); return () => clearTimeout(timer); }, [value, delay]);
  return debounced;
}
