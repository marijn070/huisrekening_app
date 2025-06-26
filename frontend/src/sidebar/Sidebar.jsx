import "./sidebar.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Link } from "react-router-dom";
import { useAccountBalances } from "../hooks/useAccountBalances";

function SideBar() {
  const { data: accountBalances } = useAccountBalances();

  const items = [
    {
      routerLink: "",
      icon: "home",
      label: "Dashboard",
    },
    {
      routerlink: "accounts",
      icon: "bank",
      label: "Accounts",
    },
    {
      routerLink: "roommates",
      icon: "users",
      label: "Roommates",
    },
    {
      routerLink: "rooms",
      icon: "door-open",
      label: "Rooms",
    },
  ];

  return (
    <div className="sidebar">
      <div className="logo-container">
        <button className="logo">
          <FontAwesomeIcon icon="bars" />
        </button>
        <div className="logo-text">App</div>
        <button className="btn-close">
          <FontAwesomeIcon icon="times" />
        </button>
      </div>
      <div>
        <div className="sidebar-nav">
          {items.map((item) => (
            <li key={item.label} className="sidebar-nav-item">
              <Link className="sidebar-nav-link" to={item.routerLink}>
                <FontAwesomeIcon
                  icon={item.icon}
                  className="sidebar-nav-icon"
                />
                <span className="sidebar-nav-text">{item.label}</span>
              </Link>
            </li>
          ))}
        </div>
      </div>
    </div>
  );
}

export default SideBar;
