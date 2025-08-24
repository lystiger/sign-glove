import React from 'react';
import './LanguageSelector.css';

const LanguageSelector = ({ 
  currentLanguage, 
  onLanguageChange, 
  showFlags = true, 
  compact = false,
  disabled = false 
}) => {
  const languages = [
    { code: 'en', name: 'English', flag: '🇺🇸', nativeName: 'English' },
    { code: 'vn', name: 'Vietnamese', flag: '🇻🇳', nativeName: 'Tiếng Việt' },
    { code: 'fr', name: 'French', flag: '🇫🇷', nativeName: 'Français' }
  ];

  const handleLanguageChange = (languageCode) => {
    if (!disabled && onLanguageChange) {
      onLanguageChange(languageCode);
    }
  };

  if (compact) {
    return (
      <div className="language-selector-compact">
        <select 
          value={currentLanguage} 
          onChange={(e) => handleLanguageChange(e.target.value)}
          disabled={disabled}
          className="language-select"
        >
          {languages.map(lang => (
            <option key={lang.code} value={lang.code}>
              {showFlags ? `${lang.flag} ` : ''}{lang.name}
            </option>
          ))}
        </select>
      </div>
    );
  }

  return (
    <div className="language-selector">
      <div className="language-buttons">
        {languages.map(lang => (
          <button
            key={lang.code}
            className={`language-btn ${currentLanguage === lang.code ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
            onClick={() => handleLanguageChange(lang.code)}
            disabled={disabled}
            title={`${lang.name} (${lang.nativeName})`}
          >
            {showFlags && <span className="flag">{lang.flag}</span>}
            <span className="name">{lang.name}</span>
            {showFlags && <span className="native-name">({lang.nativeName})</span>}
          </button>
        ))}
      </div>
    </div>
  );
};

export default LanguageSelector; 