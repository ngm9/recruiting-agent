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
              ← Back to Registration
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
        <div className="add-candidates-section">
          <h2>📱 WhatsApp Screening Registration</h2>
          <div className="form-container">
            <div className="input-form">
              <div className="input-row">
                <div className="input-group">
                  <label>Name</label>
                  <input
                    type="text"
                    name="name"
                    value={newCandidate.name}
                    onChange={handleInputChange}
                    placeholder="Enter candidate name"
                  />
                </div>

                <div className="input-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    name="phone"
                    value={newCandidate.phone}
                    onChange={handleInputChange}
                    placeholder="Enter phone number"
                  />
                </div>
              </div>

              <div className="button-group">
                <button className="add-btn" onClick={handleAddCandidate}>
                  <span>+</span> Add Candidate
                </button>
                {candidates.length > 0 && (
                  <button className="submit-btn" onClick={handleSubmitAll}>
                    <span>→</span> Begin Screening
                  </button>
                )}
              </div>
            </div>

            {candidates.length > 0 && (
              <div className="candidates-preview">
                <h3>Added Candidates ({candidates.length})</h3>
                <div className="preview-list">
                  {candidates.map((candidate, index) => (
                    <div key={index} className="preview-item">
                      <span className="preview-number">{index + 1}</span>
                      <span className="preview-name">{candidate.name}</span>
                      <span className="preview-phone">{candidate.phone}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
