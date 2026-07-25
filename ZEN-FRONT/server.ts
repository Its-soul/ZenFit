import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import dotenv from "dotenv";
import { GoogleGenAI, Type } from "@google/genai";

dotenv.config();

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json({ limit: "10mb" }));

  // Shared Gemini client instance
  const getGeminiClient = () => {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      console.warn("GEMINI_API_KEY environment variable is not set. AI features will fallback to smart mocks.");
      return null;
    }
    return new GoogleGenAI({
      apiKey,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build",
        },
      },
    });
  };

  // API Route: AI Meal Analyzer
  app.post("/api/ai/analyze-meal", async (req, res) => {
    try {
      const { mealDescription, imageBase64 } = req.body;
      const ai = getGeminiClient();

      if (!ai) {
        // Fallback response if key is missing
        return res.json({
          mealName: mealDescription || "Custom Healthy Meal",
          calories: 480,
          protein: 32,
          carbs: 45,
          fats: 16,
          insight: "Good macronutrient ratio with high protein content for muscle recovery.",
        });
      }

      const prompt = `Analyze this meal: "${mealDescription || "Meal depicted in image"}". Provide estimated calories, protein (g), carbs (g), fats (g), a title for the meal, and a brief 1-sentence nutritional insight.`;

      const contents: any[] = [];
      if (imageBase64) {
        const mimeType = imageBase64.startsWith("data:image/png") ? "image/png" : "image/jpeg";
        const cleanBase64 = imageBase64.replace(/^data:image\/\w+;base64,/, "");
        contents.push({
          inlineData: {
            mimeType,
            data: cleanBase64,
          },
        });
      }
      contents.push({ text: prompt });

      const response = await ai.models.generateContent({
        model: "gemini-3.6-flash",
        contents: { parts: contents },
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              mealName: { type: Type.STRING },
              calories: { type: Type.NUMBER },
              protein: { type: Type.NUMBER },
              carbs: { type: Type.NUMBER },
              fats: { type: Type.NUMBER },
              insight: { type: Type.STRING },
            },
            required: ["mealName", "calories", "protein", "carbs", "fats", "insight"],
          },
        },
      });

      const resultText = response.text || "{}";
      const parsed = JSON.parse(resultText);
      res.json(parsed);
    } catch (error: any) {
      console.error("Meal analysis error:", error);
      res.status(500).json({
        error: "Failed to analyze meal",
        details: error?.message || "Unknown error",
      });
    }
  });

  // API Route: AI Custom Workout Generator
  app.post("/api/ai/generate-workout", async (req, res) => {
    try {
      const { goal, duration, level, equipment } = req.body;
      const ai = getGeminiClient();

      if (!ai) {
        return res.json({
          title: `${goal || "Full Body"} Zen Routine`,
          duration: duration || "45 min",
          level: level || "Intermediate",
          category: goal || "Strength",
          description: "An adaptive high-intensity routine balanced with recovery pauses.",
          exercises: [
            { name: "Dynamic Warmup Cat-Cow", sets: 3, reps: "60 sec", rest: "15s" },
            { name: "Goblet Squats or Bodyweight Squats", sets: 4, reps: "12 reps", rest: "45s" },
            { name: "Dumbbell/Push-Up Press", sets: 4, reps: "10 reps", rest: "45s" },
            { name: "Romanian Deadlifts", sets: 3, reps: "12 reps", rest: "60s" },
            { name: "Zen Core Hold (Plank)", sets: 3, reps: "45 sec", rest: "30s" },
          ],
        });
      }

      const prompt = `Design a custom fitness routine for goal: "${goal || "Full Body Strength"}", duration: "${duration || "45 min"}", fitness level: "${level || "Intermediate"}", available equipment: "${equipment || "Dumbbells and Bodyweight"}". Return JSON with title, duration, level, category, description, and list of 5-6 exercises (each with name, sets, reps, rest).`;

      const response = await ai.models.generateContent({
        model: "gemini-3.6-flash",
        contents: prompt,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              title: { type: Type.STRING },
              duration: { type: Type.STRING },
              level: { type: Type.STRING },
              category: { type: Type.STRING },
              description: { type: Type.STRING },
              exercises: {
                type: Type.ARRAY,
                items: {
                  type: Type.OBJECT,
                  properties: {
                    name: { type: Type.STRING },
                    sets: { type: Type.NUMBER },
                    reps: { type: Type.STRING },
                    rest: { type: Type.STRING },
                  },
                  required: ["name", "sets", "reps", "rest"],
                },
              },
            },
            required: ["title", "duration", "level", "category", "description", "exercises"],
          },
        },
      });

      const parsed = JSON.parse(response.text || "{}");
      res.json(parsed);
    } catch (error: any) {
      console.error("Workout generation error:", error);
      res.status(500).json({ error: "Failed to generate workout", details: error?.message });
    }
  });

  // API Route: AI Coach Advice
  app.post("/api/ai/ask-coach", async (req, res) => {
    try {
      const { userQuery, context } = req.body;
      const ai = getGeminiClient();

      if (!ai) {
        return res.json({
          reply: "To maximize your performance today, prioritize 8 hours of quality sleep, keep your hydration above 2.5L, and focus on steady time-under-tension during your lifts.",
        });
      }

      const prompt = `You are ZenFit AI, an elite sports science & holistic recovery performance coach. User asks: "${userQuery}". User Context: ${JSON.stringify(context || {})}. Give a concise, motivating, science-backed 2-3 sentence answer.`;

      const response = await ai.models.generateContent({
        model: "gemini-3.6-flash",
        contents: prompt,
      });

      res.json({ reply: response.text || "Keep pushing steadily!" });
    } catch (error: any) {
      res.status(500).json({ error: "Failed to get coach response" });
    }
  });

  // Serve Vite in dev or static files in production
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`ZenFit server listening on http://0.0.0.0:${PORT}`);
  });
}

startServer();
