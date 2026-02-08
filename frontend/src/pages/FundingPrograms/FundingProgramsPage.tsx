import { useEffect, useState, useContext } from "react";

import { useNavigate } from "react-router-dom";
import { apiGet } from "../../utils/api";
import { AuthContext } from "../../contexts/AuthContext";
import CreateFundingProgramModal from "./CreateFundingProgramModal";

import styles from "./FundingProgramsPage.module.css";

type FundingProgram = {
  id: number;
  title: string;
  template_source: "system" | "user";
  template_ref: string;
};

export default function FundingProgramsPage() {
  const navigate = useNavigate();
  const { logout } = useContext(AuthContext);

  const [programs, setPrograms] = useState<FundingProgram[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    loadPrograms();
  }, []);

  async function loadPrograms() {
    try {
      setLoading(true);
      const data = await apiGet<FundingProgram[]>("/funding-programs");
      setPrograms(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className={styles.container}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <h2 className={styles.sidebarTitle}>Projects</h2>
        <button className={styles.sidebarItem}>
          Funding Programs
        </button>
      </aside>

      {/* Content */}
      <main className={styles.content}>
        <header className={styles.header}>
          <div className={styles.headerContent}>
            <div>
              <h1 className={styles.title}>Funding Programs</h1>
              <p className={styles.subtitle}>
                Create and manage funding program configurations.
              </p>
            </div>
            <button onClick={handleLogout} className={styles.logoutButton}>
              Logout
            </button>
          </div>
        </header>

        <section className={styles.programColumn}>
          <div className={styles.programHeader}>
            <h2 className={styles.programTitle}>Programs</h2>
            <button
              className={styles.newProgramButton}
              onClick={() => setShowCreate(true)}
            >
              + New Funding Program
            </button>
          </div>

          <div className={styles.programList}>
            {loading ? (
              <p>Loading…</p>
            ) : programs.length === 0 ? (
              <p>No funding programs yet.</p>
            ) : (
              programs.map((p) => (
                <div key={p.id} className={styles.programItem}>
                  <div>
                    <div className={styles.programName}>{p.title}</div>
                    <div className={styles.programWebsite}>
                      Template: {p.template_source}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </main>

      {showCreate && (
        <CreateFundingProgramModal
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            setShowCreate(false);
            loadPrograms();
          }}
        />
      )}
    </div>
  );
}
