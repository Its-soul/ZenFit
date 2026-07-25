export type ViewMode = 
  | 'dashboard' 
  | 'workouts' 
  | 'nutrition' 
  | 'recovery' 
  | 'progress' 
  | 'trainers' 
  | 'landing' 
  | 'settings';

export interface UserProfile {
  name: string;
  role: string;
  avatarUrl: string;
  streakDays: number;
  level: string;
}

export interface DailyGoals {
  stepsCurrent: number;
  stepsGoal: number;
  caloriesCurrent: number;
  caloriesGoal: number;
  waterCurrentL: number;
  waterGoalL: number;
}

export interface WorkoutItem {
  id: string;
  title: string;
  category: 'Strength' | 'Yoga' | 'HIIT' | 'Cardio' | 'Mobility';
  durationMinutes: number;
  level: 'Beginner' | 'Intermediate' | 'Pro';
  caloriesBurnEstimate: number;
  imageUrl: string;
  trainerName: string;
  trainerAvatar: string;
  isFavorite?: boolean;
  description: string;
  exercises: {
    name: string;
    sets: number;
    reps: string;
    rest: string;
  }[];
}

export interface MealItem {
  id: string;
  type: 'Breakfast' | 'Lunch' | 'Dinner' | 'Snacks';
  name: string;
  calories: number;
  proteinG: number;
  carbsG: number;
  fatG: number;
  time: string;
  insight?: string;
}

export interface NutritionMacroSummary {
  proteinCurrentG: number;
  proteinGoalG: number;
  carbsCurrentG: number;
  carbsGoalG: number;
  fatCurrentG: number;
  fatGoalG: number;
}

export interface SleepLog {
  id: string;
  date: string;
  hoursSlept: number;
  qualityPercentage: number;
  hrvMs: number;
  restingHeartRate: number;
  feeling: 'Drained' | 'Okay' | 'Focused' | 'Strong' | 'Motivated';
}

export interface Trainer {
  id: string;
  name: string;
  title: string;
  specialty: string;
  rating: number;
  reviewsCount: number;
  imageUrl: string;
  bio: string;
  hourlyRate: number;
  availableDays: string[];
}

export interface PersonalRecord {
  id: string;
  exercise: string;
  value: string;
  date: string;
  category: string;
}
