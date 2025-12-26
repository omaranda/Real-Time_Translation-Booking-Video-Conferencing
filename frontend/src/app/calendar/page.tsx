'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';
import Navigation from '@/components/Navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const locales = {
  'en-US': enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface Booking {
  id: string;
  translator_id: string;
  employee_id: string;
  company_id: string;
  start_time: string;
  duration_minutes: number;
  language: string;
  status: string;
  jitsi_room_name: string;
  notes: string;
  translator_name?: string;
  employee_name?: string;
  company_name?: string;
}

interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end: Date;
  resource: Booking;
}

export default function CalendarPage() {
  const router = useRouter();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [translators, setTranslators] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const { user, token, isAuthenticated, checkAuth } = useAuthStore();

  const [bookingForm, setBookingForm] = useState({
    translator_id: '',
    start_time: '',
    duration_minutes: 60,
    language: 'SPANISH',
    notes: '',
  });

  useEffect(() => {
    const initAuth = async () => {
      await checkAuth();
      if (!isAuthenticated) {
        router.push('/login');
      } else if (token) {
        fetchBookings();
        fetchTranslators();
      }
    };
    initAuth();
  }, []);

  const fetchBookings = async () => {
    try {
      const response = await axios.get(`${API_URL}/bookings/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const calendarEvents: CalendarEvent[] = response.data.map((booking: Booking) => {
        const start = new Date(booking.start_time);
        const end = new Date(start.getTime() + booking.duration_minutes * 60000);

        return {
          id: booking.id,
          title: `${booking.language} Translation - ${booking.status}`,
          start,
          end,
          resource: booking,
        };
      });

      setEvents(calendarEvents);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching bookings:', error);
      setLoading(false);
    }
  };

  const fetchTranslators = async () => {
    try {
      const response = await axios.get(`${API_URL}/translators/`, {
        params: { available_only: true },
      });
      setTranslators(response.data);
    } catch (error) {
      console.error('Error fetching translators:', error);
    }
  };

  const handleSelectEvent = (event: CalendarEvent) => {
    setSelectedEvent(event);
  };

  const handleCreateBooking = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await axios.post(`${API_URL}/bookings/`, bookingForm, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setShowBookingModal(false);
      fetchBookings();
      setBookingForm({
        translator_id: '',
        start_time: '',
        duration_minutes: 60,
        language: 'SPANISH',
        notes: '',
      });
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create booking');
    }
  };

  const joinMeeting = (booking: Booking) => {
    if (booking.jitsi_room_name) {
      const jitsiDomain = process.env.NEXT_PUBLIC_JITSI_DOMAIN || 'localhost:8443';
      const protocol = jitsiDomain.includes('localhost') ||
                      jitsiDomain.includes('127.0.0.1') ||
                      jitsiDomain.includes('.local') ||
                      jitsiDomain.includes('interpretation-service.com') ? 'http' : 'https';
      window.open(
        `${protocol}://${jitsiDomain}/${booking.jitsi_room_name}`,
        '_blank'
      );
    }
  };

  if (loading) {
    return (
      <>
        <Navigation />
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-xl text-gray-600">Loading calendar...</div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">Translation Bookings Calendar</h1>
            {(user?.role === 'EMPLOYEE' || user?.role === 'COMPANY_ADMIN') && (
              <button
                onClick={() => setShowBookingModal(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Book Translation
              </button>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow-lg" style={{ height: '700px' }}>
            <Calendar
              localizer={localizer}
              events={events}
              startAccessor="start"
              endAccessor="end"
              onSelectEvent={handleSelectEvent}
              style={{ height: '100%' }}
              views={['month', 'week', 'day']}
            />
          </div>

          {/* Event Details Modal */}
          {selectedEvent && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full">
                <h2 className="text-2xl font-bold mb-4 text-gray-800">Booking Details</h2>
                <div className="space-y-3">
                  <p className="text-gray-700">
                    <strong>Language:</strong> {selectedEvent.resource.language}
                  </p>
                  <p className="text-gray-700">
                    <strong>Duration:</strong> {selectedEvent.resource.duration_minutes} minutes
                  </p>
                  <p className="text-gray-700">
                    <strong>Status:</strong> {selectedEvent.resource.status}
                  </p>
                  <p className="text-gray-700">
                    <strong>Start Time:</strong>{' '}
                    {format(selectedEvent.start, 'PPpp')}
                  </p>
                  {selectedEvent.resource.notes && (
                    <p className="text-gray-700">
                      <strong>Notes:</strong> {selectedEvent.resource.notes}
                    </p>
                  )}
                </div>
                <div className="mt-6 flex gap-3">
                  {selectedEvent.resource.status === 'CONFIRMED' && (
                    <button
                      onClick={() => joinMeeting(selectedEvent.resource)}
                      className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
                    >
                      Join Meeting
                    </button>
                  )}
                  <button
                    onClick={() => setSelectedEvent(null)}
                    className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Booking Modal */}
          {showBookingModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full">
                <h2 className="text-2xl font-bold mb-4 text-gray-800">Book Translation Service</h2>
                <form onSubmit={handleCreateBooking} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Translator
                    </label>
                    <select
                      value={bookingForm.translator_id}
                      onChange={(e) =>
                        setBookingForm({ ...bookingForm, translator_id: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                      required
                    >
                      <option value="">Select a translator</option>
                      {translators.map((translator) => (
                        <option key={translator.id} value={translator.id}>
                          {translator.name} - {translator.languages.join(', ')}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date & Time
                    </label>
                    <input
                      type="datetime-local"
                      value={bookingForm.start_time}
                      onChange={(e) =>
                        setBookingForm({ ...bookingForm, start_time: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Duration
                    </label>
                    <select
                      value={bookingForm.duration_minutes}
                      onChange={(e) =>
                        setBookingForm({
                          ...bookingForm,
                          duration_minutes: parseInt(e.target.value),
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                      required
                    >
                      <option value="30">30 minutes</option>
                      <option value="60">1 hour</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Language
                    </label>
                    <select
                      value={bookingForm.language}
                      onChange={(e) =>
                        setBookingForm({ ...bookingForm, language: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                      required
                    >
                      <option value="SPANISH">Spanish</option>
                      <option value="FRENCH">French</option>
                      <option value="GERMAN">German</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notes (optional)
                    </label>
                    <textarea
                      value={bookingForm.notes}
                      onChange={(e) =>
                        setBookingForm({ ...bookingForm, notes: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                      rows={3}
                      placeholder="Any special requirements..."
                    />
                  </div>

                  <div className="flex gap-3 mt-6">
                    <button
                      type="submit"
                      className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                    >
                      Book Now
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowBookingModal(false)}
                      className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
