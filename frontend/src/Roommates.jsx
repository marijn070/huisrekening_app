import { useQuery } from "@tanstack/react-query";
import "./global.css";
import { useAccountBalances } from "./hooks/useAccountBalances";

const getRoommates = async () => {
  const response = await fetch(`http://localhost:8000/roommates`);
  return await response.json();
};

function RoomateCard({ roommate, balance }) {
  const formatEuro = (amount) => {
    return new Intl.NumberFormat("en-EU", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const isNegative = balance < 0;

  return (
    <div className="roommate-card">
      <div className="roommate-header">
        <div className="profile-pic-container">
          {roommate.profile_pic_url ? (
            <img
              src={roommate.profile_pic_url}
              alt={`${roommate.name}'s profile`}
              className="profile-pic"
            />
          ) : (
            <div className="profile-pic-placeholder">
              {roommate.name.charAt(0).toUpperCase()}
            </div>
          )}
        </div>
        <div className="roommate-info">
          <h3>{roommate.name}</h3>
          {roommate.email && <p>{roommate.email}</p>}
          <p className={`balance ${isNegative ? "negative" : ""}`}>
            {formatEuro(balance)}
          </p>
        </div>
      </div>
    </div>
  );
}

function Roommates() {
  const { data: roommates } = useQuery({
    queryKey: ["roommates"],
    queryFn: () => getRoommates(),
  });
  const { data: accountBalances } = useAccountBalances();

  return (
    <div className="main-content">
      <h1>Roommates</h1>
      <div className="roommates-grid">
        {roommates?.map((roommate) => (
          <RoomateCard
            key={roommate.id}
            roommate={roommate}
            balance={accountBalances?.[roommate.account.id] ?? 0}
          />
        ))}
      </div>
    </div>
  );
}

export default Roommates;
