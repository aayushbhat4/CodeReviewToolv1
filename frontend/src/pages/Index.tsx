
import { Toaster } from "sonner";
import CodeReviewForm from "@/components/CodeReviewForm";

const Index = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold text-center mb-8 text-gray-800">
            Code Reviewing Tool
          </h1>
          <div className="bg-white rounded-lg shadow-md p-6 md:p-8">
            <CodeReviewForm />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
