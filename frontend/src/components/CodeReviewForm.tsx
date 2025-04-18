import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { GitBranch, Send, RefreshCw } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface FormData {
  repoLink: string;
  codeText: string;
}

const CodeReviewForm = () => {
  const [formData, setFormData] = useState<FormData>({
    repoLink: "",
    codeText: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progressValue, setProgressValue] = useState(0);
  const [generatedResponse, setGeneratedResponse] = useState("");
  const [showResponse, setShowResponse] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.repoLink.trim()) {
      toast.error("Please enter a Git repository link");
      return false;
    }

    const gitUrlPattern = /^(https?:\/\/)?(www\.)?github\.com\/[\w.-]+\/[\w.-]+(\/?|\.git)?$/;
    if (!gitUrlPattern.test(formData.repoLink.trim())) {
      toast.error("Please enter a valid GitHub repository URL");
      return false;
    }

    if (!formData.codeText.trim()) {
      toast.error("Please enter the code you want to add");
      return false;
    }

    return true;
  };

  const simulateTypingAnimation = (text: string) => {
    let safeText = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
    let i = 0;
    setGeneratedResponse("");

    const typingInterval = setInterval(() => {
      if (i < safeText.length) {
        setGeneratedResponse((prev) => prev + safeText.charAt(i));
        i++;
      } else {
        clearInterval(typingInterval);
        setIsGenerating(false);
        setShowResponse(true);
      }
    }, 20);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);
    setIsGenerating(true);
    setProgressValue(10);

    const simulateProgress = setInterval(() => {
      setProgressValue((prev) => {
        const next = prev + Math.floor(Math.random() * 10) + 5;
        return next >= 90 ? 90 : next;
      });
    }, 300);

    try {
      const response = await fetch("http://127.0.0.1:5000/review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: formData.repoLink,
          new_code: formData.codeText,
        }),
      });

      const rawText = await response.text();
      console.log("🧪 Raw server response:", rawText);

      let data: any;
      if (!rawText.trim()) {
        toast.error("❌ Empty response from server");
        console.error("❌ Server returned empty response");
        setIsGenerating(false);
        return;
      }

      try {
        data = JSON.parse(rawText);
      } catch (err) {
        toast.error("❌ Invalid JSON from server");
        console.error("❌ JSON parse error:", err);
        setIsGenerating(false);
        return;
      }

      if (response.ok && data.feedback) {
        simulateTypingAnimation(data.feedback);
        toast.success("✅ Feedback generated successfully!");
      } else {
        setIsGenerating(false);
        toast.error(data.error || "❌ Failed to generate feedback.");
      }
    } catch (error: any) {
      console.error("Error submitting:", error);
      clearInterval(simulateProgress);
      setIsGenerating(false);
      toast.error(`An error occurred: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNewSearch = () => {
    setFormData({
      repoLink: "",
      codeText: "",
    });
    setGeneratedResponse("");
    setShowResponse(false);
    setIsGenerating(false);
    setProgressValue(0);
  };

  return (
    <div>
      {!isGenerating && !showResponse ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="repoLink" className="text-sm font-medium">
              Enter your Git repo link
            </Label>
            <div className="relative">
              <div className="absolute left-3 top-3 text-gray-500">
                <GitBranch size={18} />
              </div>
              <Input
                id="repoLink"
                name="repoLink"
                type="text"
                placeholder="https://github.com/username/repository"
                value={formData.repoLink}
                onChange={handleChange}
                className="pl-10"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="codeText" className="text-sm font-medium">
              Enter the code you want to add
            </Label>
            <Textarea
              id="codeText"
              name="codeText"
              placeholder="Paste your code here..."
              value={formData.codeText}
              onChange={handleChange}
              rows={12}
              className="font-mono text-sm resize-y"
            />
          </div>

          <Button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              "Submitting..."
            ) : (
              <span className="flex items-center justify-center gap-2">
                Submit <Send size={16} />
              </span>
            )}
          </Button>
        </form>
      ) : (
        <div className="space-y-6">
          {isGenerating && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-center text-blue-600">
                Generating your code feedback...
              </h2>
              <Progress className="w-full h-2" value={progressValue} />
            </div>
          )}

          {generatedResponse && (
            <div className="mt-6 space-y-4">
              <div className="bg-gray-50 p-4 rounded-md border border-gray-200 overflow-x-auto">
                <pre className="font-mono text-sm whitespace-pre-wrap break-words">
                  {generatedResponse}
                </pre>
              </div>

              {showResponse && (
                <Button
                  onClick={handleNewSearch}
                  className="w-full mt-4 bg-green-600 hover:bg-green-700 text-white"
                >
                  <span className="flex items-center justify-center gap-2">
                    New Search <RefreshCw size={16} />
                  </span>
                </Button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CodeReviewForm;
