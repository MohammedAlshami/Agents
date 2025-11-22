"""
Humanize Agent Improvement Script
Iteratively tests and improves the humanize agent by generating paragraphs,
detecting AI content, humanizing when needed, and modifying prompts when performance is poor.
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from tqdm import tqdm

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from writer_agent import WriterAgent
from zerogpt_detector import ZeroGPTDetector
from prompt_modifier import PromptModifier


class HumanizeAgentImprover:
    """
    Main class for improving the humanize agent through iterative testing.
    """
    
    def __init__(
        self,
        humanize_api_url: str,
        openai_api_key: str = None,
        topics: List[str] = None,
        success_threshold: int = 3,
        failure_threshold: int = 5,  # Changed default to 5 for modification interval
        ai_detection_threshold: float = 35.0
    ):
        """
        Initialize the improver.
        
        Args:
            humanize_api_url: URL of the humanize API endpoint
            openai_api_key: OpenAI API key for writer agent and prompt modifier
            topics: List of topics for paragraph generation
            success_threshold: Number of consecutive 0% results needed to stop (default: 3)
            failure_threshold: Number of attempts before modifying prompts (default: 5)
            ai_detection_threshold: AI detection percentage threshold for humanization (default: 35%)
        """
        self.humanize_api_url = humanize_api_url
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.topics = topics or self._get_default_topics()
        self.success_threshold = success_threshold
        self.modification_interval = failure_threshold  # Reuse failure_threshold parameter as modification_interval
        self.ai_detection_threshold = ai_detection_threshold
        
        # Initialize components
        self.writer_agent = WriterAgent(api_key=self.openai_api_key)
        self.zerogpt_detector = ZeroGPTDetector()
        self.prompt_modifier = PromptModifier(api_key=self.openai_api_key)
        
        # Track state
        self.results: List[Dict[str, Any]] = []
        self.consecutive_successes = 0
        self.consecutive_failures = 0
        self.attempt_count = 0
        
    def _get_default_topics(self) -> List[str]:
        """Get default list of topics for paragraph generation."""
        return [
            "The impact of artificial intelligence on modern business",
            "Climate change and its effects on global economies",
            "The future of remote work",
            "Sustainable energy solutions",
            "Digital transformation in healthcare",
            "The role of social media in society",
            "Renewable energy technologies",
            "Cybersecurity challenges in 2024",
            "The evolution of e-commerce",
            "Machine learning applications in finance"
        ]
    
    def call_humanize_api(self, text: str) -> Dict[str, Any]:
        """
        Call the humanize API endpoint.
        
        Args:
            text: Text to humanize
            
        Returns:
            Dict with humanized text and metadata
        """
        try:
            response = requests.post(
                self.humanize_api_url,
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "humanized_text": ""
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "humanized_text": ""
            }
    
    def process_paragraph_iteratively(self, topic: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Process a single paragraph with iterative improvement:
        Generate → Detect → Humanize → Improve Prompts → Repeat up to 5 times
        
        Args:
            topic: Topic for paragraph generation
            max_iterations: Maximum number of improvement iterations (default: 5)
            
        Returns:
            Dict with complete processing results including all iterations
        """
        result = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "iterations": [],
            "best_ai_percent": 100.0,
            "final_paragraph": "",
            "final_ai_percent": 100.0
        }
        
        # Step 1: Generate initial paragraph
        print(f"\n{'='*80}")
        print(f"Topic: {topic}")
        print(f"{'='*80}")
        with tqdm(desc="Generating paragraph", leave=False) as pbar:
            write_result = self.writer_agent.generate_paragraph(topic)
            pbar.update(1)
        
        if not write_result["success"]:
            result["error"] = write_result.get("error", "Failed to generate paragraph")
            print(f"ERROR: {result['error']}")
            return result
        
        current_paragraph = write_result["paragraph"]
        result["original_paragraph"] = current_paragraph
        print(f"\nGenerated Paragraph ({len(current_paragraph)} chars):")
        print(f"{'-'*80}")
        print(current_paragraph[:200] + "..." if len(current_paragraph) > 200 else current_paragraph)
        print(f"{'-'*80}")
        
        # Step 2: Initial AI detection
        print("\nDetecting AI in original text...")
        with tqdm(desc="Detecting AI", leave=False) as pbar:
            detection = self.zerogpt_detector.detect_text(current_paragraph)
            pbar.update(1)
        
        current_ai_percent = detection.get("ai_probability", 0)
        result["original_ai_percent"] = current_ai_percent
        result["best_ai_percent"] = current_ai_percent
        
        print(f"\n{'='*80}")
        print(f"INITIAL AI DETECTION: {current_ai_percent:.2f}%")
        print(f"{'='*80}")
        
        # Track iteration history
        iteration_history = []
        
        # Iterative improvement loop (up to 5 times)
        for iteration in range(1, max_iterations + 1):
            iteration_result = {
                "iteration": iteration,
                "paragraph": current_paragraph,
                "ai_percent_before": current_ai_percent,
                "ai_percent_after": current_ai_percent,
                "humanized": False,
                "prompts_modified": False
            }
            
            print(f"\n{'='*80}")
            print(f"ITERATION {iteration}/{max_iterations}")
            print(f"{'='*80}")
            print(f"Current AI%: {current_ai_percent:.2f}%")
            
            # Check if we've achieved success
            if current_ai_percent == 0.0:
                print("SUCCESS! Achieved 0% AI detection.")
                result["success"] = True
                result["final_paragraph"] = current_paragraph
                result["final_ai_percent"] = 0.0
                iteration_result["success"] = True
                iteration_history.append(iteration_result)
                break
            
            # Step 3: Humanize (always if not at 0%)
            if current_ai_percent > 0.0:
                print(f"\nHumanizing text (iteration {iteration})...")
                with tqdm(desc="Humanizing", leave=False) as pbar:
                    humanize_result = self.call_humanize_api(current_paragraph)
                    pbar.update(1)
                
                if humanize_result.get("success", False):
                    current_paragraph = humanize_result.get("humanized_text", current_paragraph)
                    iteration_result["humanized"] = True
                    iteration_result["paragraph"] = current_paragraph
                    
                    # Re-detect after humanization
                    print("Re-detecting AI after humanization...")
                    with tqdm(desc="Re-detecting AI", leave=False) as pbar:
                        detection = self.zerogpt_detector.detect_text(current_paragraph)
                        pbar.update(1)
                    
                    current_ai_percent = detection.get("ai_probability", 0)
                    iteration_result["ai_percent_after"] = current_ai_percent
                    
                    print(f"AI% after humanization: {current_ai_percent:.2f}%")
                    
                    # Update best if improved
                    if current_ai_percent < result["best_ai_percent"]:
                        result["best_ai_percent"] = current_ai_percent
                        print(f"New best AI%: {current_ai_percent:.2f}%")
                else:
                    print(f"Warning: Humanization failed: {humanize_result.get('error', 'Unknown error')}")
            
            # Step 4: Improve prompts AFTER humanization (for next iteration)
            if current_ai_percent > 0.0 and iteration < max_iterations:  # Don't improve on last iteration if we're done
                print(f"\nImproving prompts (iteration {iteration})...")
                
                # Create attempt data for this iteration with full context
                attempt_data = [{
                    "topic": topic,
                    "original_ai_percent": result["original_ai_percent"],
                    "humanized_ai_percent": current_ai_percent,
                    "success": current_ai_percent == 0.0,
                    "original_paragraph": result["original_paragraph"],
                    "humanized_paragraph": current_paragraph,
                    "iteration": iteration,
                    "improvement": result["original_ai_percent"] - current_ai_percent,
                    "best_ai_percent": result["best_ai_percent"]
                }]
                
                # Search Perplexity and modify prompts
                print("Step 1: Searching Perplexity for latest humanization tips...")
                with tqdm(desc="Searching Perplexity", leave=False) as pbar:
                    # Actual search happens inside analyze_and_modify
                    pbar.update(1)
                
                print("Step 2: Analyzing and modifying prompts with research findings...")
                with tqdm(desc="Analyzing and modifying", leave=False) as pbar:
                    modification_result = self.prompt_modifier.analyze_and_modify(attempt_data)
                    pbar.update(1)
                
                if modification_result.get("success"):
                    if not iteration_result.get("prompts_modified"):
                        iteration_result["prompts_modified"] = True
                        iteration_result["modified_prompt"] = modification_result.get("prompt_modified")
                    print(f"\n✓ Modified prompt: {modification_result.get('prompt_modified')}")
                    print(f"Reasoning: {modification_result.get('reasoning', '')[:300]}...")
                    print(f"Note: Next iteration will use the updated prompts.")
                else:
                    print(f"\n✗ Warning: Prompt modification failed: {modification_result.get('error', 'Unknown error')}")
            
            iteration_history.append(iteration_result)
            
            # Check if we achieved success in this iteration
            if current_ai_percent == 0.0:
                result["success"] = True
                result["final_paragraph"] = current_paragraph
                result["final_ai_percent"] = 0.0
                break
        
        # Final state
        result["iterations"] = iteration_history
        result["final_paragraph"] = current_paragraph
        result["final_ai_percent"] = current_ai_percent
        result["humanized_ai_percent"] = current_ai_percent  # For compatibility
        
        # Display final summary
        print(f"\n{'='*80}")
        print("FINAL RESULT:")
        print(f"{'='*80}")
        print(f"Original AI%: {result['original_ai_percent']:.2f}%")
        print(f"Final AI%: {result['final_ai_percent']:.2f}%")
        print(f"Best AI% achieved: {result['best_ai_percent']:.2f}%")
        print(f"Total iterations: {len(iteration_history)}")
        print(f"Success: {'YES' if result['success'] else 'NO'} (Required: 0.00%)")
        print(f"{'='*80}\n")
        
        return result
    
    def run(self) -> Dict[str, Any]:
        """
        Run the improvement loop with iterative paragraph refinement.
        Each paragraph is improved up to 5 times with prompt modifications.
        
        Returns:
            Dict with final results and statistics
        """
        print("Starting Humanize Agent Improvement Process")
        print(f"Success threshold: {self.success_threshold} consecutive 0% results")
        print(f"Iterations per paragraph: {self.modification_interval}")
        print(f"AI detection threshold: {self.ai_detection_threshold}%")
        print(f"Improvement cycle: Generate → Detect → Humanize → Improve Prompts → Repeat")
        print("-" * 80)
        
        paragraph_count = 0
        topic_index = 0
        
        # Main loop - process paragraphs until we get 3 consecutive successes
        with tqdm(desc="Improvement Progress", unit="paragraph") as main_pbar:
            while self.consecutive_successes < self.success_threshold:
                paragraph_count += 1
                
                # Get topic (cycle through topics)
                topic = self.topics[topic_index % len(self.topics)]
                topic_index += 1
                
                main_pbar.set_description(
                    f"Paragraph {paragraph_count} | "
                    f"Successes: {self.consecutive_successes}/{self.success_threshold} | "
                    f"Topic: {topic[:30]}..."
                )
                
                # Process paragraph with iterative improvement
                result = self.process_paragraph_iteratively(topic, max_iterations=self.modification_interval)
                self.results.append(result)
                
                # Update counters based on final result
                if result["success"]:
                    self.consecutive_successes += 1
                    self.consecutive_failures = 0
                    main_pbar.set_postfix({
                        "Status": "SUCCESS",
                        "AI%": f"{result['final_ai_percent']:.1f}%",
                        "Iterations": len(result.get('iterations', []))
                    })
                else:
                    self.consecutive_successes = 0
                    self.consecutive_failures += 1
                    main_pbar.set_postfix({
                        "Status": "FAILED",
                        "AI%": f"{result.get('final_ai_percent', 0):.1f}%",
                        "Best": f"{result.get('best_ai_percent', 0):.1f}%",
                        "Iterations": len(result.get('iterations', []))
                    })
                
                main_pbar.update(1)
                
                # Prevent infinite loop (safety limit)
                if paragraph_count >= 100:
                    print("\nSafety limit reached (100 paragraphs). Stopping.")
                    break
        
        # Generate final statistics
        total_paragraphs = len(self.results)
        successful_paragraphs = sum(1 for r in self.results if r["success"])
        success_rate = (successful_paragraphs / total_paragraphs * 100) if total_paragraphs > 0 else 0
        
        # Calculate total iterations across all paragraphs
        total_iterations = sum(len(r.get("iterations", [])) for r in self.results)
        
        avg_original_ai = sum(r.get("original_ai_percent", 0) for r in self.results) / total_paragraphs if total_paragraphs > 0 else 0
        avg_final_ai = sum(r.get("final_ai_percent", 0) for r in self.results) / total_paragraphs if total_paragraphs > 0 else 0
        avg_best_ai = sum(r.get("best_ai_percent", 100) for r in self.results) / total_paragraphs if total_paragraphs > 0 else 100
        
        final_results = {
            "completed": True,
            "total_paragraphs": total_paragraphs,
            "successful_paragraphs": successful_paragraphs,
            "success_rate": success_rate,
            "total_iterations": total_iterations,
            "average_iterations_per_paragraph": total_iterations / total_paragraphs if total_paragraphs > 0 else 0,
            "consecutive_successes": self.consecutive_successes,
            "average_original_ai_percent": avg_original_ai,
            "average_final_ai_percent": avg_final_ai,
            "average_best_ai_percent": avg_best_ai,
            "timestamp": datetime.now().isoformat(),
            "results": self.results
        }
        
        return final_results
    
    def save_results(self, filename: str = "humanize_improvement_results.json"):
        """
        Save results to JSON file.
        
        Args:
            filename: Output filename
        """
        total_iterations = sum(len(r.get("iterations", [])) for r in self.results)
        output = {
            "summary": {
                "total_paragraphs": len(self.results),
                "successful_paragraphs": sum(1 for r in self.results if r["success"]),
                "total_iterations": total_iterations,
                "average_iterations_per_paragraph": total_iterations / len(self.results) if self.results else 0,
                "consecutive_successes": self.consecutive_successes,
                "consecutive_failures": self.consecutive_failures
            },
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {filename}")


def load_config(config_file: str = "improve_config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Dict with configuration values
    """
    default_config = {
        "humanize_api_url": "http://localhost:5004/api/v1/humanize/",
        "openai_api_key": None,
        "topics": None,
        "success_threshold": 3,
        "modification_interval": 5,
        "ai_detection_threshold": 35.0,
        "output_file": "humanize_improvement_results.json"
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
            print("Using default configuration.")
            return default_config
    
    return default_config


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Improve the humanize agent through iterative testing"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="improve_config.json",
        help="Path to configuration JSON file (default: improve_config.json)"
    )
    
    parser.add_argument(
        "--humanize-api-url",
        type=str,
        default=None,
        help="URL of the humanize API endpoint (overrides config)"
    )
    
    parser.add_argument(
        "--openai-api-key",
        type=str,
        default=None,
        help="OpenAI API key (or set OPENAI_API_KEY env var, overrides config)"
    )
    
    parser.add_argument(
        "--topics",
        type=str,
        nargs="+",
        default=None,
        help="List of topics for paragraph generation (overrides config)"
    )
    
    parser.add_argument(
        "--success-threshold",
        type=int,
        default=None,
        help="Number of consecutive 0%% results needed to stop (default: 3, overrides config)"
    )
    
    parser.add_argument(
        "--modification-interval",
        type=int,
        default=None,
        help="Number of attempts before modifying prompts (default: 5, overrides config)"
    )
    
    parser.add_argument(
        "--ai-detection-threshold",
        type=float,
        default=None,
        help="AI detection percentage threshold for humanization (default: 35.0%%, overrides config)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output filename for results (overrides config)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command-line arguments if provided
    humanize_api_url = args.humanize_api_url or config.get("humanize_api_url")
    openai_api_key = args.openai_api_key or config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
    topics = args.topics or config.get("topics")
    success_threshold = args.success_threshold if args.success_threshold is not None else config.get("success_threshold", 3)
    modification_interval = args.modification_interval if args.modification_interval is not None else config.get("modification_interval", config.get("failure_threshold", 5))
    ai_detection_threshold = args.ai_detection_threshold if args.ai_detection_threshold is not None else config.get("ai_detection_threshold", 35.0)
    output_file = args.output or config.get("output_file", "humanize_improvement_results.json")
    
    # Create improver
    improver = HumanizeAgentImprover(
        humanize_api_url=humanize_api_url,
        openai_api_key=openai_api_key,
        topics=topics,
        success_threshold=success_threshold,
        failure_threshold=modification_interval,  # Pass as failure_threshold parameter (used as modification_interval internally)
        ai_detection_threshold=ai_detection_threshold
    )
    
    # Run improvement process
    try:
        final_results = improver.run()
        
        # Print summary
        print("\n" + "=" * 80)
        print("IMPROVEMENT PROCESS COMPLETED")
        print("=" * 80)
        print(f"Total paragraphs processed: {final_results['total_paragraphs']}")
        print(f"Successful paragraphs: {final_results['successful_paragraphs']}")
        print(f"Success rate: {final_results['success_rate']:.2f}%")
        print(f"Total iterations: {final_results['total_iterations']}")
        print(f"Average iterations per paragraph: {final_results['average_iterations_per_paragraph']:.2f}")
        print(f"Consecutive successes: {final_results['consecutive_successes']}")
        print(f"Average original AI%: {final_results['average_original_ai_percent']:.2f}%")
        print(f"Average final AI%: {final_results['average_final_ai_percent']:.2f}%")
        print(f"Average best AI% achieved: {final_results['average_best_ai_percent']:.2f}%")
        print("=" * 80)
        
        # Save results
        improver.save_results(output_file)
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        improver.save_results(output_file)
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during improvement process: {e}")
        improver.save_results(output_file)
        raise


if __name__ == "__main__":
    main()

