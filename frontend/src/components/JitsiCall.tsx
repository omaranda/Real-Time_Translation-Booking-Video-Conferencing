'use client';

import { useEffect, useRef, useState } from 'react';

interface JitsiCallProps {
  roomName: string;
  displayName?: string;
  onCallEnd?: () => void;
  onParticipantJoined?: (participant: any) => void;
  onParticipantLeft?: (participant: any) => void;
}

declare global {
  interface Window {
    JitsiMeetExternalAPI: any;
  }
}

export default function JitsiCall({
  roomName,
  displayName = 'Agent',
  onCallEnd,
  onParticipantJoined,
  onParticipantLeft,
}: JitsiCallProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const apiRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load Jitsi External API script
    const loadJitsiScript = () => {
      if (window.JitsiMeetExternalAPI) {
        initializeJitsi();
        return;
      }

      const domain = process.env.NEXT_PUBLIC_JITSI_DOMAIN || 'localhost:8443';
      const script = document.createElement('script');
      // Use HTTP for local development (localhost and .local domains), HTTPS for production
      const isLocal = domain.includes('localhost') ||
                     domain.includes('127.0.0.1') ||
                     domain.includes('.local') ||
                     domain.includes('interpretation-service.com');
      const protocol = isLocal ? 'http' : 'https';
      script.src = `${protocol}://${domain}/external_api.js`;
      script.async = true;
      script.onload = () => initializeJitsi();
      script.onerror = () => {
        console.error(`Failed to load Jitsi External API. Make sure Jitsi is running on ${domain}`);
        setIsLoading(false);
      };
      document.body.appendChild(script);
    };

    const initializeJitsi = () => {
      if (!containerRef.current || apiRef.current) return;

      const domain = process.env.NEXT_PUBLIC_JITSI_DOMAIN || 'localhost:8443';

      const options = {
        roomName: roomName,
        width: '100%',
        height: '100%',
        parentNode: containerRef.current,
        userInfo: {
          displayName: displayName,
        },
        configOverwrite: {
          startWithAudioMuted: false,
          startWithVideoMuted: false,
          enableWelcomePage: false,
          prejoinPageEnabled: false,
        },
        interfaceConfigOverwrite: {
          SHOW_JITSI_WATERMARK: false,
          SHOW_WATERMARK_FOR_GUESTS: false,
          TOOLBAR_BUTTONS: [
            'microphone',
            'camera',
            'desktop',
            'hangup',
            'chat',
            'settings',
            'raisehand',
            'videoquality',
            'tileview',
            'download',
            'help',
            'mute-everyone',
          ],
        },
      };

      apiRef.current = new window.JitsiMeetExternalAPI(domain, options);

      // Event listeners
      apiRef.current.addListener('videoConferenceJoined', () => {
        setIsLoading(false);
      });

      apiRef.current.addListener('videoConferenceLeft', () => {
        onCallEnd?.();
      });

      apiRef.current.addListener('participantJoined', (participant: any) => {
        onParticipantJoined?.(participant);
      });

      apiRef.current.addListener('participantLeft', (participant: any) => {
        onParticipantLeft?.(participant);
      });
    };

    loadJitsiScript();

    return () => {
      if (apiRef.current) {
        apiRef.current.dispose();
        apiRef.current = null;
      }
    };
  }, [roomName, displayName, onCallEnd, onParticipantJoined, onParticipantLeft]);

  return (
    <div className="relative w-full h-full">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
          <div className="text-white text-lg">Connecting to call...</div>
        </div>
      )}
      <div ref={containerRef} className="w-full h-full" />
    </div>
  );
}
