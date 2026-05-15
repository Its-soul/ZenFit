import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";

export default function SettingsPage() {
  return (
    <ProtectedFeaturePage
      title="Settings"
      description="Profile, preferences, units, notifications, and future integrations will live here."
    >
      <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-muted">
        Profile basics are already stored during onboarding.
      </div>
    </ProtectedFeaturePage>
  );
}

