import { motion } from "framer-motion";
import { LuFileText, LuClock, LuUsers, LuGlobe } from "react-icons/lu";

export default function Sidebar({ metadata, highlights }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <motion.div
          className="sidebar-glow"
          animate={{ opacity: [0.4, 0.9, 0.4] }}
          transition={{ duration: 6, repeat: Infinity }}
        />
        <h1>AI Research Adviser</h1>
        <p>Transform documents into actionable business insights.</p>
      </div>

      {metadata && (
        <section className="sidebar-card">
          <h3>Document Overview</h3>
          <ul>
            <li>
              <LuFileText /> <span>{metadata.filename}</span>
            </li>
            <li>
              <LuClock /> <span>{metadata.word_count} words</span>
            </li>
            {metadata.language && (
              <li>
                <LuGlobe /> <span>{metadata.language}</span>
              </li>
            )}
            {metadata.parties.length > 0 && (
              <li className="sidebar-inline">
                <LuUsers />
                <div>
                  {metadata.parties.map((party) => (
                    <span key={party} className="sidebar-chip">
                      {party}
                    </span>
                  ))}
                </div>
              </li>
            )}
            {metadata.dates.length > 0 && (
              <li>
                <LuClock /> <span>Key dates: {metadata.dates.slice(0, 2).join(", ")}</span>
              </li>
            )}
          </ul>
        </section>
      )}

      {highlights.length > 0 && (
        <section className="sidebar-card">
          <h3>Rapid Highlights</h3>
          <div className="sidebar-highlights">
            {highlights.map((highlight, index) => (
              <motion.div
                key={highlight.title + index}
                className="highlight-card"
                whileHover={{ translateY: -4, scale: 1.01 }}
              >
                <h4>{highlight.title}</h4>
                <p>{highlight.snippet}</p>
                <span>{highlight.rationale}</span>
              </motion.div>
            ))}
          </div>
        </section>
      )}
    </aside>
  );
}

