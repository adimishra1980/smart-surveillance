import express, { Request } from "express";
import cors from "cors";
import multer from "multer";
import axois from "axios";
import FormData from "form-data";
import fs from "fs";

const app = express();
const upload = multer({ dest: "uploads/" });

app.use(
  cors({
    origin: "*",
  }),
);
app.use(express.json());

app.post(
  "/detect",
  upload.single("image"),
  // async (req: Request, res: Response) => {
  //   try {
        
  //   } catch (error) {
        
  //   }
  // },
);

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});
