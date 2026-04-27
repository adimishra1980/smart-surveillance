import express, { Request, Response } from "express";
import dotenv from "dotenv";
import cors from "cors";

import detectionsRoutes from "./routes/detections.routes";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(
  cors({
    origin: "*",
  }),
);
app.use(express.json({ limit: "10mb" }));

// Routes
app.use("/detections", detectionsRoutes);

// Health check
app.get("/health", (_req: Request, res: Response) => {
  res.json({ status: "ok", service: "api-backend" });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
