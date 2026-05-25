import "./globals.css";

export const metadata = {
  title: "ZenFit",
  description: "Your adaptive daily fitness coach"
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
