import "./globals.css";

export const metadata = {
  title: "AI Fitness OS",
  description: "Adaptive AI-first fitness operating system"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

