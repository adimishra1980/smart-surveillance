import { Request, Response } from "express";
import db from "../db";
import { sessionParamsSchema } from "../validations/sessions.validations";

const getSessions = async (_req: Request, res: Response) => {
  try {
    const sessions = await db.detectionSession.findMany({
      orderBy: { startedAt: "desc" },
      include: {
        _count: { select: { detections: true } },
      },
    });

    return res.json(
      sessions.map((s) => ({
        id: s.id,
        source: s.source,
        startedAt: s.startedAt,
        totalDetections: s._count.detections,
      })),
    );
  } catch {
    return res.status(500).json({ error: "Failed to fetch sessions" });
  }
};

// GET /api/sessions/:id
const getSessionById = async (req: Request, res: Response) => {
  const parsed = sessionParamsSchema.safeParse(req.params);

  if (!parsed.success) {
    return res.status(400).json({
      error: "Invalid session ID",
      details: parsed.error.flatten(),
    });
  }

  const { id } = parsed.data;
  try {
    const session = await db.detectionSession.findUnique({
      where: { id },
      include: {
        _count: { select: { detections: true } },
        detections: {
          orderBy: { detectedAt: "desc" },
          take: 100,
        },
      },
    });

    if (!session) {
      return res.status(404).json({ error: "Session not found" });
    }

    return res.json(session);
  } catch {
    return res.status(500).json({ error: "Failed to fetch session" });
  }
};

export { getSessions, getSessionById };
