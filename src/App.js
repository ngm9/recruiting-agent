import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [candidates, setCandidates] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [newCandidate, setNewCandidate] = useState({
    name: '',
    phone: ''
  });

  useEffect(() => {
    let intervalId;
    
    if (showLeaderboard) {
      updateLeaderboard();
      
      intervalId = setInterval(updateLeaderboard, 5000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [showLeaderboard]);

  const updateLeaderboard = () => {
    const reportData = require('./report.json');
    const candidatesWithScores = reportData.map(report => ({
      name: report.name,
      phone: '',
      score: Math.round((report.total / 40) * 100)
    }));

    const sortedCandidates = candidatesWithScores
      .sort((a, b) => b.score - a.score)
      .map((candidate, index) => ({
        ...candidate,
        rank: index + 1
      }));

    setLeaderboard(sortedCandidates);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewCandidate(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAddCandidate = () => {
    
    if (!newCandidate.name || !newCandidate.phone) return;
    
    setCandidates(prev => [...prev, newCandidate]);
    setNewCandidate({ name: '', phone: '' });
  };

  const handleSubmitAll = () => {
    
    updateLeaderboard();
    setShowLeaderboard(true);
  };

  if (showLeaderboard) {
    return (
      <div className="App">
        <div className="container">
          <div className="leaderboard-header">
            <h2>📊 Candidate Interest Analysis</h2>
            <button className="back-btn" onClick={() => setShowLeaderboard(false)}>
              ← Back to Job Details
            </button>
          </div>
          
          <div className="leaderboard-section">
            <div className="leaderboard-stats">
              <div className="stat-card">
                <span className="stat-number">{leaderboard.length}</span>
                <span className="stat-label">Screened Candidates</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {Math.max(...leaderboard.map(c => c.score))}%
                </span>
                <span className="stat-label">Highest Interest Score</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {leaderboard.filter(c => c.score >= 70).length}
                </span>
                <span className="stat-label">High Potential Matches</span>
              </div>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Name</th>
                  <th>Phone</th>
                  <th>Interest Score</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((candidate, index) => (
                  <tr key={index} className={candidate.score >= 70 ? 'top-rank' : ''}>
                    <td>
                      {candidate.rank <= 3 ? 
                        <span className={`rank-badge rank-${candidate.rank}`}>
                          {candidate.rank}
                        </span> : 
                        candidate.rank
                      }
                    </td>
                    <td>{candidate.name}</td>
                    <td>{candidate.phone}</td>
                    <td>
                      <div className="score-wrapper">
                        <div className="score-bar" style={{width: `${candidate.score}%`}}></div>
                        <span>{candidate.score}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="score-legend">
              <div className="legend-item">
                <span className="legend-color high"></span>
                <span>High Interest (70-100%)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color medium"></span>
                <span>Medium Interest (40-69%)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color low"></span>
                <span>Low Interest (0-39%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <div className="container">
        <div className="position-details-section">
          <div className="position-header">
            <h2>🎯 Position Details</h2>
            <div className="position-badge">Active</div>
          </div>
          <div className="details-container">
            <div className="detail-card">
              <div className="detail-icon">👨‍💻</div>
              <div className="detail-content">
                <label>Position</label>
                <span>React Developer - 1</span>
              </div>
            </div>
            
            <div className="detail-card">
              <div className="detail-icon">📍</div>
              <div className="detail-content">
                <label>Location</label>
                <span>Vadodara, Gujarat</span>
              </div>
            </div>

            <div className="detail-card">
              <div className="detail-icon">💰</div>
              <div className="detail-content">
                <label>Salary Range</label>
                <span>4 LPA - 6 LPA</span>
              </div>
            </div>

            <div className="detail-card">
              <div className="detail-icon">⚡</div>
              <div className="detail-content">
                <label>Required Skills</label>
                <div className="skills-container">
                  <span className="skill-tag">ReactJS</span>
                  <span className="skill-tag">JavaScript</span>
                  <span className="skill-tag">HTML/CSS</span>
                </div>
              </div>
            </div>

            <div className="detail-card">
              <div className="detail-icon">⏳</div>
              <div className="detail-content">
                <label>Experience</label>
                <span>0-2 years</span>
              </div>
            </div>
            
            <button className="view-leaderboard-btn" onClick={() => setShowLeaderboard(true)}>
              View Candidate Analysis 
              <span className="button-icon">→</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
