import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => location.pathname === path ? "nav-link active" : "nav-link";

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-brand">
          <span className="brand-icon">💊</span>
          <span className="brand-text">HealthMate <span className="brand-ai">AI</span></span>
        </Link>

        <div className="nav-links">
          <Link to="/about" className={isActive("/about")}>About</Link>
          {user && (
            <>
              <Link to="/scan" className={isActive("/scan")}>Scan</Link>
              <Link to="/history" className={isActive("/history")}>History</Link>
              {user.role === "admin" && (
                <Link to="/admin" className={isActive("/admin")}>Admin</Link>
              )}
            </>
          )}
        </div>

        <div className="nav-auth">
          {user ? (
            <div className="user-menu">
              <span className="user-name">{user.name}</span>
              <span className="user-badge">{user.role}</span>
              <button className="btn btn-ghost" onClick={handleLogout}>Logout</button>
            </div>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">Login</Link>
              <Link to="/register" className="btn btn-primary">Sign Up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
