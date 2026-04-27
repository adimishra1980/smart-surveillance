import { z } from "zod";

const sessionParamsSchema = z.object({
  id: z.string().min(1, "Session ID is required"),
});

export { sessionParamsSchema };
