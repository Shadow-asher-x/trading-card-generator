import React, { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [useUploadedImage, setUseUploadedImage] = useState(false);
  const [cardData, setCardData] = useState({
    name: 'Mystery Creature',
    hp: 100,
    type: 'Fire',
    rarity: 'Common',
    flavorText: 'A mysterious creature from the depths...',
    attacks: [
      { name: 'Flame Strike', damage: 30, description: 'Burns the enemy with intense flames' },
      { name: 'Fire Shield', damage: 0, description: 'Reduces incoming damage by 10' }
    ]
  });

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedImage(e.target.result);
        setUseUploadedImage(true);
      };
      reader.readAsDataURL(file);
    }
  };

  const generateImage = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    setUseUploadedImage(false);
    try {
      const response = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setGeneratedImage(data.image_url);
        if (data.metadata) {
          setCardData(prev => ({
            ...prev,
            ...data.metadata
          }));
        }
      } else {
        console.error('Failed to generate image');
      }
    } catch (error) {
      console.error('Error generating image:', error);
    }
    setIsGenerating(false);
  };

  const downloadCard = async () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = 720;
    canvas.height = 1000;
    
    const currentImg = getCurrentImage();
    if (!currentImg) {
      const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      gradient.addColorStop(0, '#667eea');
      gradient.addColorStop(1, '#764ba2');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    const rarityColors = {
      'common': '#9ca3af',
      'uncommon': '#10b981', 
      'rare': '#3b82f6',
      'epic': '#8b5cf6',
      'legendary': '#f59e0b'
    };
    
    ctx.strokeStyle = rarityColors[cardData.rarity.toLowerCase()] || '#9ca3af';
    ctx.lineWidth = 8;
    ctx.strokeRect(4, 4, canvas.width - 8, canvas.height - 8);
    
    const headerGradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
    headerGradient.addColorStop(0, 'rgba(0, 0, 0, 0.85)');
    headerGradient.addColorStop(0.7, 'rgba(0, 0, 0, 0.6)');
    headerGradient.addColorStop(1, 'rgba(0, 0, 0, 0.4)');
    ctx.fillStyle = headerGradient;
    ctx.fillRect(0, 0, canvas.width, 80);
    
    ctx.fillStyle = 'white';
    ctx.font = 'bold 36px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(cardData.name, 30, 55);
    
    ctx.fillStyle = '#ef4444';
    ctx.textAlign = 'right';
    ctx.fillText(`HP ${cardData.hp}`, canvas.width - 100, 55);
    
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(canvas.width - 50, 40, 25, 0, 2 * Math.PI);
    ctx.fill();
    
    ctx.fillStyle = 'black';
    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(getTypeSymbol(cardData.type), canvas.width - 50, 48);
    
    let yPos = canvas.height - 200;
    cardData.attacks.forEach((attack, index) => {
      ctx.fillStyle = 'white';
      ctx.beginPath();
      ctx.arc(50, yPos, 20, 0, 2 * Math.PI);
      ctx.fill();
      
      ctx.fillStyle = 'black';
      ctx.font = 'bold 24px Arial';
      ctx.textAlign = 'center';
      ctx.fillText((index + 1).toString(), 50, yPos + 8);
      
      ctx.fillStyle = 'black';
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 3;
      ctx.font = 'bold 32px Arial';
      ctx.textAlign = 'left';
      ctx.strokeText(attack.name, 90, yPos + 8);
      ctx.fillText(attack.name, 90, yPos + 8);
      
      if (attack.damage > 0) {
        ctx.fillStyle = '#ef4444';
        ctx.textAlign = 'right';
        ctx.fillText(attack.damage.toString(), canvas.width - 30, yPos + 8);
      }
      
      ctx.fillStyle = 'black';
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 2;
      ctx.font = '24px Arial';
      ctx.textAlign = 'left';
      ctx.strokeText(attack.description, 90, yPos + 40);
      ctx.fillText(attack.description, 90, yPos + 40);
      
      yPos += 80;
    });
    
    ctx.fillStyle = 'black';
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.font = 'italic 20px Arial';
    ctx.textAlign = 'center';
    ctx.strokeText(cardData.flavorText, canvas.width / 2, canvas.height - 60);
    ctx.fillText(cardData.flavorText, canvas.width / 2, canvas.height - 60);
    
    ctx.fillStyle = 'black';
    ctx.font = 'bold 18px Arial';
    ctx.textAlign = 'right';
    ctx.strokeText(cardData.rarity, canvas.width - 30, canvas.height - 20);
    ctx.fillText(cardData.rarity, canvas.width - 30, canvas.height - 20);
    
    const link = document.createElement('a');
    link.download = `${cardData.name.replace(/\s+/g, '_')}_card.jpg`;
    link.href = canvas.toDataURL('image/jpeg', 0.9);
    link.click();
  };

  const updateCardData = (field, value) => {
    setCardData(prev => ({ ...prev, [field]: value }));
  };

  const updateAttack = (index, field, value) => {
    setCardData(prev => ({
      ...prev,
      attacks: prev.attacks.map((attack, i) => 
        i === index ? { ...attack, [field]: value } : attack
      )
    }));
  };

  const getCurrentImage = () => {
    if (useUploadedImage && uploadedImage) return uploadedImage;
    if (generatedImage) return generatedImage;
    return null;
  };

  const getTypeSymbol = (type) => {
    const symbols = {
      'Fire': 'F',
      'Water': 'W', 
      'Earth': 'E',
      'Air': 'A',
      'Dark': 'D',
      'Light': 'L'
    };
    return symbols[type] || 'N';
  };

  return (
    <div className="app">
      <h1>Trading Card Generator</h1>
      
      <div className="main-container">
        <div className="controls-panel">
          <h2>Create Your Card</h2>
          
          <div className="input-group">
            <label>Describe your creature:</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A fierce dragon with crystalline scales, breathing blue fire..."
              rows={3}
            />
            <button onClick={generateImage} disabled={isGenerating || !prompt.trim()}>
              {isGenerating ? 'Generating...' : 'Generate AI Image'}
            </button>
          </div>

          <div className="input-group">
            <label>Or upload your own image:</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              style={{ 
                padding: '8px',
                background: 'rgba(255, 255, 255, 0.2)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '8px',
                color: 'white'
              }}
            />
            {uploadedImage && (
              <p style={{ color: 'white', fontSize: '14px', marginTop: '5px' }}>
                ✓ Image uploaded successfully
              </p>
            )}
          </div>

          <div className="card-inputs">
            <div className="input-row">
              <div className="input-group">
                <label>Name:</label>
                <input
                  value={cardData.name}
                  onChange={(e) => updateCardData('name', e.target.value)}
                />
              </div>
              <div className="input-group">
                <label>HP:</label>
                <input
                  type="number"
                  value={cardData.hp}
                  onChange={(e) => updateCardData('hp', parseInt(e.target.value))}
                />
              </div>
            </div>

            <div className="input-row">
              <div className="input-group">
                <label>Type:</label>
                <select value={cardData.type} onChange={(e) => updateCardData('type', e.target.value)}>
                  <option value="Fire">Fire</option>
                  <option value="Water">Water</option>
                  <option value="Earth">Earth</option>
                  <option value="Air">Air</option>
                  <option value="Dark">Dark</option>
                  <option value="Light">Light</option>
                </select>
              </div>
              <div className="input-group">
                <label>Rarity:</label>
                <select value={cardData.rarity} onChange={(e) => updateCardData('rarity', e.target.value)}>
                  <option value="Common">Common</option>
                  <option value="Uncommon">Uncommon</option>
                  <option value="Rare">Rare</option>
                  <option value="Epic">Epic</option>
                  <option value="Legendary">Legendary</option>
                </select>
              </div>
            </div>

            <div className="input-group">
              <label>Flavor Text:</label>
              <textarea
                value={cardData.flavorText}
                onChange={(e) => updateCardData('flavorText', e.target.value)}
                rows={2}
              />
            </div>

            <div className="attacks-section">
              <label>Attacks:</label>
              {cardData.attacks.map((attack, index) => (
                <div key={index} className="attack-input">
                  <div className="attack-row">
                    <input
                      placeholder="Attack name"
                      value={attack.name}
                      onChange={(e) => updateAttack(index, 'name', e.target.value)}
                    />
                    <input
                      type="number"
                      placeholder="Damage"
                      value={attack.damage}
                      onChange={(e) => updateAttack(index, 'damage', parseInt(e.target.value))}
                      style={{ width: '80px' }}
                    />
                  </div>
                  <textarea
                    placeholder="Attack description"
                    value={attack.description}
                    onChange={(e) => updateAttack(index, 'description', e.target.value)}
                    rows={1}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="card-preview">
          <h2>Card Preview</h2>
          
          <div 
            className={`trading-card ${cardData.rarity.toLowerCase()} ${getCurrentImage() ? 'has-image' : ''}`}
            style={getCurrentImage() ? {
              backgroundImage: `url(${getCurrentImage()})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            } : {}}
          >
            <div className="card-header">
              <h3>{cardData.name}</h3>
              <div className="card-header-right">
                <div className="hp">HP {cardData.hp}</div>
                <div className={`type-icon ${cardData.type.toLowerCase()}`}>
                  {getTypeSymbol(cardData.type)}
                </div>
              </div>
            </div>

            {!getCurrentImage() && (
              <div className="card-image">
                <div className="placeholder">
                  <p>Generate an image or upload your own to see your creature here</p>
                </div>
              </div>
            )}

            <div className="card-bottom">
              <div className="attacks">
                {cardData.attacks.map((attack, index) => (
                  <div key={index} className="attack">
                    <div className="attack-header">
                      <div className="attack-info">
                        <div className="energy-cost">{index + 1}</div>
                        <span className="attack-name">{attack.name}</span>
                      </div>
                      {attack.damage > 0 && <span className="damage">{attack.damage}</span>}
                    </div>
                    <p className="attack-description">{attack.description}</p>
                  </div>
                ))}
              </div>

              <div className="flavor-text">
                {cardData.flavorText}
              </div>
            </div>

            <div className="rarity">
              {cardData.rarity}
            </div>
          </div>

          <button onClick={downloadCard} className="download-btn">
            Download Card as JPEG
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;