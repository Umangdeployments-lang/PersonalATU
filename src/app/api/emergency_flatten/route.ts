import { NextResponse } from "next/server";

export async function POST() {
  // Trigger emergency flatten
  return NextResponse.json({ success: true, message: "Emergency flatten triggered" });
}