import AiImg from "@/assets/notebookbg/ai.jpg";
import EducationImg from "@/assets/notebookbg/education.jpg";
import UnionBudgetImg from "@/assets/notebookbg/unionbudget.png";

const defaultImg = EducationImg;

export const getNotebookImage = (title?: string) => {
  if (!title) return defaultImg.src;

  const t = title.toLowerCase();

  if (t.includes("education") || t.includes("academic"))
    return EducationImg.src;

  if (
    t.includes("digital") ||
    t.includes("governance") ||
    t.includes("cyber") ||
    t.includes("it")
  )
    return AiImg.src;

  if (t.includes("union") || t.includes("budget"))
    return UnionBudgetImg.src;

  return defaultImg.src;
};