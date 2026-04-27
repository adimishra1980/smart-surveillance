import { z } from "zod";

const detectionSchema = z.object({
  object: z.string(),
  confidence: z.number(),
  bounding_box: z.object({
    x1: z.number(),
    y1: z.number(),
    x2: z.number(),
    y2: z.number(),
  }),
});

const requestSchema = z.object({
  timestamp: z.union([z.string(), z.number()]).optional(),
  source: z.string().optional(),
  sessionId: z.string(),
  detections: z.array(detectionSchema),
});

export { detectionSchema, requestSchema };
