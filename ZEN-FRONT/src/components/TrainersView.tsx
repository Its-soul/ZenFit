import React, { useState } from 'react';
import { 
  Users, 
  Star, 
  Calendar, 
  Clock, 
  MessageSquare, 
  CheckCircle2, 
  X, 
  Award,
  Sparkles
} from 'lucide-react';
import { Trainer } from '../types';

interface TrainersViewProps {
  trainers: Trainer[];
}

export const TrainersView: React.FC<TrainersViewProps> = ({ trainers }) => {
  const [selectedTrainer, setSelectedTrainer] = useState<Trainer | null>(null);
  const [bookingDate, setBookingDate] = useState('2026-03-20');
  const [bookingTime, setBookingTime] = useState('10:00 AM');
  const [notes, setNotes] = useState('');
  const [bookingSuccess, setBookingSuccess] = useState(false);

  const handleBookSession = (e: React.FormEvent) => {
    e.preventDefault();
    setBookingSuccess(true);
    setTimeout(() => {
      setBookingSuccess(false);
      setSelectedTrainer(null);
      setNotes('');
    }, 2000);
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800/80 p-6 md:p-8 shadow-xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold">
              <Award className="w-3.5 h-3.5" />
              <span>Elite Bio-Mechanics & Coaches</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-slate-100 tracking-tight">
              Train with World-Class Master Coaches
            </h2>
            <p className="text-xs md:text-sm text-slate-400 leading-relaxed">
              Book 1-on-1 virtual or hybrid biomechanics evaluations, custom meal strategy consultations, and lifting form audits.
            </p>
          </div>
        </div>
      </div>

      {/* Trainers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {trainers.map((trainer) => (
          <div
            key={trainer.id}
            className="bg-slate-900/80 border border-slate-800/80 hover:border-emerald-500/40 rounded-3xl overflow-hidden shadow-xl transition-all duration-300 flex flex-col justify-between group"
          >
            <div>
              <div className="relative h-56 overflow-hidden bg-slate-950">
                <img
                  src={trainer.imageUrl}
                  alt={trainer.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />

                <div className="absolute top-3 right-3 bg-slate-950/80 backdrop-blur-md px-2.5 py-1 rounded-xl border border-slate-800 flex items-center gap-1 text-xs font-bold text-amber-400">
                  <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                  <span>{trainer.rating.toFixed(1)}</span>
                  <span className="text-slate-500 text-[10px]">({trainer.reviewsCount})</span>
                </div>
              </div>

              <div className="p-5 space-y-3">
                <div>
                  <h3 className="text-base font-bold text-slate-100 group-hover:text-emerald-300 transition-colors">
                    {trainer.name}
                  </h3>
                  <p className="text-xs font-semibold text-emerald-400 mt-0.5">{trainer.title}</p>
                </div>

                <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {trainer.bio}
                </p>

                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
                  <span className="text-slate-400">Specialty</span>
                  <span className="font-bold text-slate-200">{trainer.specialty}</span>
                </div>
              </div>
            </div>

            <div className="p-5 pt-0 space-y-2">
              <div className="flex items-center justify-between text-xs pb-2">
                <span className="text-slate-400">Rate</span>
                <span className="text-sm font-black text-slate-100 font-mono">${trainer.hourlyRate}/hr</span>
              </div>

              <button
                id={`book-trainer-${trainer.id}`}
                onClick={() => setSelectedTrainer(trainer)}
                className="w-full py-2.5 px-4 rounded-xl font-bold text-xs bg-emerald-400 hover:bg-emerald-300 text-slate-950 transition-all flex items-center justify-center gap-1.5 shadow-md shadow-emerald-500/10"
              >
                <Calendar className="w-3.5 h-3.5" />
                <span>Book Consultation</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Booking Modal */}
      {selectedTrainer && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 space-y-6 shadow-2xl relative animate-fade-in">
            <button
              onClick={() => setSelectedTrainer(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            {bookingSuccess ? (
              <div className="py-8 text-center space-y-3">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-black text-slate-100">Consultation Confirmed!</h3>
                <p className="text-xs text-slate-400">
                  Your session with <strong className="text-white">{selectedTrainer.name}</strong> on {bookingDate} at {bookingTime} has been added to your ZenFit calendar.
                </p>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-4 border-b border-slate-800 pb-4">
                  <img
                    src={selectedTrainer.imageUrl}
                    alt={selectedTrainer.name}
                    className="w-14 h-14 rounded-2xl object-cover ring-2 ring-emerald-500/30"
                  />
                  <div>
                    <h3 className="text-lg font-bold text-slate-100">{selectedTrainer.name}</h3>
                    <p className="text-xs text-emerald-400 font-semibold">{selectedTrainer.title}</p>
                    <p className="text-[11px] text-slate-400">${selectedTrainer.hourlyRate}/hr • {selectedTrainer.specialty}</p>
                  </div>
                </div>

                <form onSubmit={handleBookSession} className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-300 mb-1">Select Date</label>
                      <input
                        type="date"
                        value={bookingDate}
                        onChange={(e) => setBookingDate(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-slate-300 mb-1">Time Slot</label>
                      <select
                        value={bookingTime}
                        onChange={(e) => setBookingTime(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                      >
                        <option value="09:00 AM">09:00 AM</option>
                        <option value="10:00 AM">10:00 AM</option>
                        <option value="02:00 PM">02:00 PM</option>
                        <option value="05:00 PM">05:00 PM</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Session Goal / Notes</label>
                    <textarea
                      rows={3}
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Describe what you want to address (e.g. Squat biomechanics, HRV fatigue, diet structure)"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full py-3 px-4 rounded-xl font-bold text-xs bg-emerald-400 hover:bg-emerald-300 text-slate-950 transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Confirm Booking (${selectedTrainer.hourlyRate})</span>
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
