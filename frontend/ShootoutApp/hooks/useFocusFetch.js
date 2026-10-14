import { useCallback, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';

// Fetches on screen focus (so lists stay fresh after joining) and supports pull-to-refresh.
export default function useFocusFetch(fetcher, deps = []) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      setData(await fetcher());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useFocusEffect(useCallback(() => { setLoading(true); load(); }, [load]));
  const refresh = () => { setRefreshing(true); load(); };
  return { data, loading, refreshing, error, reload: load, refresh };
}
