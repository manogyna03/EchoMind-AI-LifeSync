import { useState, useEffect, useCallback } from 'react';

// Helper to select a voice based on gender preference (default male)
function selectVoice(gender: 'male' | 'female' = 'male'): SpeechSynthesisVoice | null {
  const voices = window.speechSynthesis.getVoices();
  const englishVoices = voices.filter(v => v.lang.startsWith('en'));
  if (englishVoices.length === 0) {
    console.warn('No English voices available for speech synthesis.');
    return null;
  }
  // Simple keyword matching for gender
  const maleKeywords = /male|david|john|alex|mike|ryan|kevin|william|tom|paul|mark|steve|bob|james|jason|eric|patrick|chris|charles|stephen|sam|ron|greg|tim|jeff|dan|scott|luke|brian|donald|johnny|jerry|harry|noah|leo|rich/i;
  const femaleKeywords = /female|samantha|amy|julia|emma|lisa|karen|anna|sarah|laura|michelle|maria|jennifer|mary|susan|diana|rebecca|olivia|linda|patricia|jessica|nicole|kelly|chloe|alice|rachel|kate|nancy|sharon|sylvia|violet|eve/i;
  const regex = gender === 'male' ? maleKeywords : femaleKeywords;
  const matching = englishVoices.find(v => regex.test(v.name.toLowerCase()));
  if (matching) {
    return matching;
  }
  // Fallback to first English voice
  console.warn(`Preferred ${gender} English voice not found. Falling back to first available English voice.`);
  return englishVoices[0] || null;
}

export function useVoice() {
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [gender, setGender] = useState<'male' | 'female'>('male');

  // Initialize on mount – wait for voices if needed
  useEffect(() => {
    if (!('speechSynthesis' in window)) {
      console.warn('Speech synthesis not supported in this browser.');
      return;
    }
    const init = () => {
      const saved = (localStorage.getItem('preferredVoiceGender') as 'male' | 'female') || 'male';
      setGender(saved);
      const voice = selectVoice(saved);
      setSelectedVoice(voice);
    };
    if (window.speechSynthesis.getVoices().length > 0) {
      init();
    } else {
      window.speechSynthesis.onvoiceschanged = () => init();
    }
  }, []);

  const setPreferredGender = useCallback((g: 'male' | 'female') => {
    localStorage.setItem('preferredVoiceGender', g);
    setGender(g);
    const voice = selectVoice(g);
    setSelectedVoice(voice);
  }, []);

  const speak = useCallback((text: string) => {
    if (!('speechSynthesis' in window)) {
      console.warn('Speech synthesis not supported.');
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    } else {
      // Try to pick a fallback now
      const fallback = selectVoice(gender);
      if (fallback) {
        utterance.voice = fallback;
        setSelectedVoice(fallback);
      }
    }
    window.speechSynthesis.speak(utterance);
  }, [selectedVoice, gender]);

  return { selectedVoice, gender, setPreferredGender, speak };
}
