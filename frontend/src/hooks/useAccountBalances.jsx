import { useQuery } from "@tanstack/react-query";
import { fetchAllBalances } from "../api/accounts";

export function useAccountBalances() {
  return useQuery({
    queryKey: ["accountBalances"],
    queryFn: fetchAllBalances,
    staleTime: 1000 * 5, // e.g. 5 seconds
  });
}
