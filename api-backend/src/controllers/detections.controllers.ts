import { Request, Response } from "express";
import db from "../db";
import { requestSchema } from "../validations/detections.validations";

// helper function
const safeDate = (timestamp?: string | number) => {
  if (!timestamp) return new Date();
  const d = new Date(timestamp);
  return isNaN(d.getTime()) ? new Date() : d;
};

// POST /detections
export const createDetections = async (req: Request, res: Response) => {
  const parsed = requestSchema.safeParse(req.body);

  if (!parsed.success) {
    return res.status(400).json({
      error: "Invalid payload",
      details: parsed.error.flatten(),
    });
  }

  const { timestamp, detections, source, sessionId } = parsed.data;

  try {
    // Upsert session (better than find+create)
    const session = await db.detectionSession.upsert({
      where: { id: sessionId },
      update: {},
      create: {
        id: sessionId,
        source: source || "unknown",
      },
    });

    if (detections.length === 0) {
      return res.json({ saved: 0 });
    }

    const detectedAt = safeDate(timestamp);

    // Batch insert (fast)
    const result = await db.detection.createMany({
      data: detections.map((d) => ({
        sessionId: session.id,
        object: d.object,
        confidence: d.confidence,
        x1: d.bounding_box.x1,
        y1: d.bounding_box.y1,
        x2: d.bounding_box.x2,
        y2: d.bounding_box.y2,
        detectedAt,
      })),
      skipDuplicates: true, // prevents duplicates
    });

    return res.json({
      saved: result.count,
      sessionId: session.id,
    });
  } catch (error) {
    console.error("[Detections] Error:", error);
    return res.status(500).json({ error: "Failed to save detections" });
  }
};

// GET /detections
export const getDetections = async (req: Request, res: Response) => {
  const { object, sessionId, limit = "50" } = req.query;

  const take = Math.min(parseInt(String(limit)) || 50, 500); // cap limit

  try {
    const detections = await db.detection.findMany({
      where: {
        ...(object ? { object: String(object) } : {}),
        ...(sessionId ? { sessionId: String(sessionId) } : {}),
      },
      orderBy: { detectedAt: "desc" },
      take,
      include: {
        session: {
          select: { source: true, startedAt: true },
        },
      },
    });

    return res.json(detections);
  } catch {
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
  } catch {
    return res.status(500).json({ error: "Failed to fetch stats" });
  }
};
