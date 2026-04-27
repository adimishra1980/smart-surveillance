import { Router } from "express";
import {
  createDetections,
  getDetections,
  getDetectionStats,
} from "../controllers/detections.controllers";

const router = Router();

router.post("/", createDetections);
router.get("/", getDetections);
router.get("/stats", getDetectionStats);

export default router;
