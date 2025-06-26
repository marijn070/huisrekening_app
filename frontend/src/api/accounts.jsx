export async function fetchAllBalances() {
  const response = await fetch("http://localhost:8000/account-balances");
  const data = await response.json();
  return data;
}
