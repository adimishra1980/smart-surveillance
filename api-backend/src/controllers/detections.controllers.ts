import { Request, Response } from "express";
import db from "../db";

// POST /detections
export const createDetections = async (req: Request, res: Response) => {
  const { timestamp, detections, source, sessionId } = req.body;

  if (!detections || !Array.isArray(detections)) {
    return res.status(400).json({ error: "detections array required" });
  }

  try {
    let session = await db.detectionSession.findUnique({
      where: { id: sessionId },
    });

    if (!session) {
      session = await db.detectionSession.create({
        data: {
          id: sessionId,
          source: source || "unknown",
        },
      });
    }

    if (detections.length === 0) {
      return res.json({ saved: 0 });
    }

    await db.detection.createMany({
      data: detections.map((d: any) => ({
        sessionId: session!.id,
        object: d.object,
        confidence: d.confidence,
        x1: d.bounding_box.x1,
        y1: d.bounding_box.y1,
        x2: d.bounding_box.x2,
        y2: d.bounding_box.y2,
        detectedAt: new Date(timestamp),
      })),
    });

    return res.json({
      saved: detections.length,
      sessionId: session.id,
    });
  } catch (error) {
    console.error("[Detections] Error saving:", error);
    return res.status(500).json({ error: "Failed to save detections" });
  }
};

// GET /detections
export const getDetections = async (req: Request, res: Response) => {
  const { object, sessionId, limit = "50" } = req.query;

  try {
    const detections = await db.detection.findMany({
      where: {
        ...(object ? { object: String(object) } : {}),
        ...(sessionId ? { sessionId: String(sessionId) } : {}),
      },
      orderBy: { detectedAt: "desc" },
      take: parseInt(String(limit)),
      include: {
        session: {
          select: { source: true, startedAt: true },
        },
      },
    });

    return res.json(detections);
  } catch (error) {
    return res.status(500).json({ error: "Failed to fetch detections" });
  }
};

// GET /detections/stats
export const getDetectionStats = async (_req: Request, res: Response) => {
  try {
    const [total, byObject, sessions] = await Promise.all([
      db.detection.count(),
      db.detection.groupBy({
        by: ["object"],
        _count: { object: true },
        orderBy: { _count: { object: "desc" } },
      }),
      db.detectionSession.count(),
    ]);

    return res.json({
      total_detections: total,
      total_sessions: sessions,
      by_object: byObject.map((b) => ({
        object: b.object,
        count: b._count.object,
      })),
    });
  } catch (error) {
    return res.status(500).json({ error: "Failed to fetch stats" });
  }
};
