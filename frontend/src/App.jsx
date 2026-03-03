import React, { useState, useEffect, useRef, useMemo } from 'react'
import axios from 'axios'
import { Mic, MicOff, Volume2, VolumeX, StopCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const API_BASE = 'http://localhost:8001'

function App() {
  const [isMuted, setIsMuted] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isTalking, setIsTalking] = useState(false)
  const [status, setStatus] = useState('Idle')
  const [transcript, setTranscript] = useState('')

  const audioRef = useRef(new Audio())
  const recognitionRef = useRef(null)

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  // Initialize MediaRecorder for Voice Input
  useEffect(() => {
    async function initMediaRecorder() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        mediaRecorderRef.current = new MediaRecorder(stream)

        mediaRecorderRef.current.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data)
          }
        }

        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
          audioChunksRef.current = [] // reset

          setStatus('Transcribing...')

          try {
            const formData = new FormData()
            formData.append('file', audioBlob, 'recording.webm')

            const sttResponse = await axios.post(`${API_BASE}/stt`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            })

            const text = sttResponse.data.text
            setTranscript(text)
            setStatus(`Interpreting: "${text}"`)
            handleChat(text)
          } catch (err) {
            console.error('STT Error:', err)
            setStatus('Error during transcription.')
          }
        }
      } catch (err) {
        console.error('Error accessing microphone:', err)
        setStatus('Microphone access denied.')
      }
    }

    initMediaRecorder()
  }, [])

  const toggleListening = () => {
    if (isListening) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop()
      }
      setIsListening(false)
    } else {
      audioRef.current.pause() // Stop any ongoing TTS
      setIsTalking(false)
      setTranscript('')
      setStatus('Listening...')
      setIsListening(true)

      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'inactive') {
        audioChunksRef.current = []
        mediaRecorderRef.current.start()
      }
    }
  }

  const handleChat = (text) => {
    if (isMuted) {
      // Fallback if muted, though we should probably still handle history
      return
    }

    try {
      setStatus('Prompting...')
      setIsTalking(true)

      // Use the unified streaming endpoint directly
      // This sends the prompt and starts receiving the audio stream immediately
      const audioUrl = `${API_BASE}/chat_voice?prompt=${encodeURIComponent(text)}&t=${Date.now()}`

      console.log('Streaming from:', audioUrl)
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current.src = audioUrl

      const playPromise = audioRef.current.play()
      if (playPromise !== undefined) {
        playPromise.catch(err => {
          console.error('Streaming Playback failed:', err)
          setStatus('Playback Error')
          setIsTalking(false)
        })
      }

      audioRef.current.onplay = () => {
        setStatus('Streaming Voice...')
      }

      audioRef.current.onended = () => {
        setIsTalking(false)
        setStatus('Idle')
      }

      audioRef.current.onerror = (e) => {
        console.error("Streaming Audio error:", e)
        setStatus("Stream Error.")
        setIsTalking(false)
      }

    } catch (err) {
      console.error('Chat handle error:', err)
      setStatus('Error connecting to backend.')
      setIsTalking(false)
    }
  }

  const playTTS = async (text) => {
    try {
      setIsTalking(true)
      setStatus('Responding...')

      const audioUrl = `${API_BASE}/tts_stream?text=${encodeURIComponent(text)}&t=${Date.now()}`
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current.src = audioUrl

      const playPromise = audioRef.current.play()
      if (playPromise !== undefined) {
        playPromise.catch(err => {
          console.error('Playback failed:', err)
          setStatus('Playback Error')
          setIsTalking(false)
        })
      }

      audioRef.current.onended = () => {
        setIsTalking(false)
        setStatus('Idle')
      }

      audioRef.current.onerror = (e) => {
        console.error("Audio error:", e)
        setStatus("Audio Stream Error.")
        setIsTalking(false)
      }
    } catch (err) {
      console.error('TTS Playback error:', err)
      setIsTalking(false)
      setStatus('Error in TTS.')
    }
  }

  const toggleMute = () => {
    setIsMuted(!isMuted)
    if (!isMuted) {
      audioRef.current.pause()
      setIsTalking(false)
    }
  }



  return (
    <div className="app-container">
      <div className="ripple-wrapper">
        <motion.div
          className="core-ring"
          animate={isTalking ? {
            scale: [1, 1.05, 1],
            boxShadow: [
              '0 0 30px var(--primary-color), inset 0 0 15px var(--primary-color)',
              '0 0 50px var(--primary-color), inset 0 0 25px var(--primary-color)',
              '0 0 30px var(--primary-color), inset 0 0 15px var(--primary-color)'
            ]
          } : (isListening ? { scale: 1.15 } : { scale: 1 })}
          transition={isTalking ? { repeat: Infinity, duration: 2 } : {}}
        >
          <div className="core-inner" />
        </motion.div>

        {/* Ripple Rings */}
        <AnimatePresence>
          {isTalking && (
            <>
              {[1, 2, 3].map((i) => (
                <motion.div
                  key={`ripple-${i}`}
                  className="ripple"
                  initial={{ scale: 1, opacity: 0.5 }}
                  animate={{
                    scale: 2.5,
                    opacity: 0,
                  }}
                  transition={{
                    repeat: Infinity,
                    duration: 2.5,
                    delay: i * 0.8,
                    ease: "easeOut"
                  }}
                />
              ))}
            </>
          )}
        </AnimatePresence>

        {isListening && !isTalking && (
          <motion.div
            className="ripple"
            initial={{ scale: 1, opacity: 0.3 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{ repeat: Infinity, duration: 1.5, ease: "easeOut" }}
          />
        )}
      </div>

      <div className="controls">
        <button
          className={`btn btn-mute ${isMuted ? 'muted' : ''}`}
          onClick={toggleMute}
          title={isMuted ? 'Unmute' : 'Mute Sound'}
        >
          {isMuted ? <VolumeX /> : <Volume2 />}
          {isMuted ? 'Sound Off' : 'Mute'}
        </button>

        <button
          className={`btn btn-input ${isListening ? 'active' : ''}`}
          onClick={toggleListening}
          title={isListening ? 'Stop Listening' : 'Start Input'}
        >
          {isListening ? <StopCircle /> : <Mic />}
          {isListening ? 'Stop Voice' : 'Input'}
        </button>
      </div>

      <div className="status">
        {status}
      </div>

      {transcript && (
        <div style={{ marginTop: '10px', fontSize: '0.8rem', opacity: 0.6 }}>
          Last input: "{transcript}"
        </div>
      )}
    </div>
  )
}

export default App
