#!/usr/bin/env python3
"""
Text Quality Tests for the Omni-Converter.

This module tests the quality of text extraction for different file types
using BLEU, ROUGE-L, and structural preservation metrics.
"""

import os
import json
import tempfile
import unittest
from datetime import datetime
from typing import Dict, List, Any, Union, Tuple, Optional
from collections import Counter
import re

import nltk
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
from nltk.tokenize import word_tokenize, sent_tokenize
from rouge_score import rouge_scorer

from core.processing_pipeline import processing_pipeline
from core.validator import BasicValidator, make_validator
from configs import Configs, configs

# Download required NLTK data
nltk.download('punkt', quiet=True)


# =============================================================================
# METRIC IMPLEMENTATIONS (Composable Functions)
# =============================================================================

def calculate_bleu_score(reference: str, hypothesis: str, 
                        weights: Tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)) -> float:
    """
    Calculate BLEU score between reference and hypothesis texts.
    
    Args:
        reference: Reference (ground truth) text
        hypothesis: Generated/extracted text to evaluate
        weights: Weights for n-gram precisions (default: equal weights for 1-4 grams)
        
    Returns:
        BLEU score between 0 and 1
    """
    # Tokenize texts
    reference_tokens = word_tokenize(reference.lower())
    hypothesis_tokens = word_tokenize(hypothesis.lower())
    
    # Handle empty texts
    if not reference_tokens or not hypothesis_tokens:
        return 0.0
    
    # Calculate BLEU score
    try:
        score = sentence_bleu([reference_tokens], hypothesis_tokens, weights=weights)
        return float(score)
    except:
        # Handle cases where n-gram order exceeds text length
        return 0.0


def calculate_corpus_bleu_score(references: List[str], hypotheses: List[str],
                               weights: Tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)) -> float:
    """
    Calculate corpus-level BLEU score.
    
    Args:
        references: List of reference texts
        hypotheses: List of hypothesis texts
        weights: Weights for n-gram precisions
        
    Returns:
        Corpus-level BLEU score
    """
    # Tokenize all texts
    references_tokens = [[word_tokenize(ref.lower())] for ref in references]
    hypotheses_tokens = [word_tokenize(hyp.lower()) for hyp in hypotheses]
    
    # Calculate corpus BLEU
    try:
        score = corpus_bleu(references_tokens, hypotheses_tokens, weights=weights)
        return float(score)
    except:
        return 0.0


def calculate_rouge_l_score(reference: str, hypothesis: str) -> Dict[str, float]:
    """
    Calculate ROUGE-L scores between reference and hypothesis texts.
    
    Args:
        reference: Reference text
        hypothesis: Hypothesis text
        
    Returns:
        Dictionary with precision, recall, and f1 scores
    """
    # Initialize ROUGE scorer
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=False)
    
    # Calculate scores
    scores = scorer.score(reference, hypothesis)
    
    return {
        'precision': scores['rougeL'].precision,
        'recall': scores['rougeL'].recall,
        'f1': scores['rougeL'].fmeasure
    }


def calculate_structural_preservation_score(reference: str, hypothesis: str) -> float:
    """
    Calculate structural preservation score between reference and hypothesis texts.
    Measures preservation of paragraphs, sections, lists, and tables.
    
    Args:
        reference: Reference text
        hypothesis: Hypothesis text
        
    Returns:
        Structural preservation score between 0 and 1
    """
    def extract_structural_elements(text: str) -> Dict[str, int]:
        """Extract counts of structural elements from text."""
        elements = {
            'paragraphs': 0,
            'sections': 0,
            'lists': 0,
            'tables': 0,
            'headers': 0
        }
        
        # Count paragraphs (separated by double newlines)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        elements['paragraphs'] = len(paragraphs)
        
        # Count sections/headers (lines starting with #, ending with :, or all caps)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # Markdown headers
                if line.startswith('#'):
                    elements['headers'] += 1
                    elements['sections'] += 1
                # Colon-ended headers
                elif line.endswith(':') and len(line) < 100 and not line.startswith(('*', '-', '•')):
                    elements['headers'] += 1
                # All caps headers (at least 3 chars)
                elif line.isupper() and len(line) >= 3 and line.replace(' ', '').isalpha():
                    elements['headers'] += 1
        
        # Count lists (lines starting with *, -, •, or numbered)
        list_pattern = re.compile(r'^[\*\-•]|\d+\.')
        for line in lines:
            if list_pattern.match(line.strip()):
                elements['lists'] += 1
        
        # Count tables (lines containing |)
        table_lines = [line for line in lines if '|' in line and line.count('|') >= 2]
        if table_lines:
            # Group consecutive table lines as one table
            elements['tables'] = 1
            for i in range(1, len(table_lines)):
                if lines.index(table_lines[i]) - lines.index(table_lines[i-1]) > 1:
                    elements['tables'] += 1
        
        return elements
    
    # Extract structural elements from both texts
    ref_elements = extract_structural_elements(reference)
    hyp_elements = extract_structural_elements(hypothesis)
    
    # Calculate preservation score for each element type
    preservation_scores = []
    
    for element_type in ref_elements:
        ref_count = ref_elements[element_type]
        hyp_count = hyp_elements[element_type]
        
        if ref_count == 0:
            # If reference has no elements of this type, score is 1 if hypothesis also has none
            score = 1.0 if hyp_count == 0 else 0.0
        else:
            # Calculate preservation ratio, capped at 1.0
            score = min(hyp_count / ref_count, 1.0)
        
        preservation_scores.append(score)
    
    # Return average preservation score
    return sum(preservation_scores) / len(preservation_scores) if preservation_scores else 0.0


def calculate_text_quality_factor(
        bleu: float, 
        rouge_l: float, 
        structural: Optional[float] = None,
        alpha: float = 0.5, 
        beta: float = 0.3, 
        gamma: float = 0.2
        ) -> float:
    """
    Calculate overall text quality factor using weighted combination of metrics.
    
    Args:
        bleu: BLEU score
        rouge_l: ROUGE-L F1 score
        structural: Structural preservation score (optional)
        alpha: Weight for BLEU score
        beta: Weight for ROUGE-L score
        gamma: Weight for structural preservation (only used if structural is provided)
        
    Returns:
        Text quality factor between 0 and 1
    """
    if structural is not None:
        # Text and Application categories use all three metrics
        return alpha * bleu + beta * rouge_l + gamma * structural
    else:
        # Image, Audio, Video categories use only BLEU and ROUGE-L
        # Normalize weights to sum to 1
        total_weight = alpha + beta
        return (alpha / total_weight) * bleu + (beta / total_weight) * rouge_l


# =============================================================================
# TEST DATA MANAGEMENT
# =============================================================================

class TestDataManager:
    """Manages test files and ground truth data."""
    from pathlib import Path

    def __init__(self, 
                 test_files_dir: str = 'test_files'
                 ):
        self.test_files_dir = configs.paths.ROOT_DIR / test_files_dir
        self.ground_truth_dirs = [
            (self.test_files_dir / 'ground_truth').resolve(),
            (self.test_files_dir / 'reference').resolve()
        ]
        
        # Define format categories
        self.format_categories = {
            'text': ['html', 'xml', 'txt', 'csv', 'ics', 'md'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
            'audio': ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'],
            'video': ['mp4', 'webm', 'avi', 'mkv', 'mov'],
            'application': ['pdf', 'json', 'zip', 'docx', 'xlsx', 'pptx']
        }
    
    def find_test_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """Find all test files with corresponding ground truth."""
        test_files = {category: [] for category in self.format_categories}
        
        if not self.test_files_dir.exists():
            return test_files
        
        # Search for test files
        for category, formats in self.format_categories.items():
            # Check category subdirectory
            category_dir = (self.test_files_dir / category).resolve()
            self._find_files_in_directory(category_dir, category, formats, test_files)
            
            # Also check main test_files directory
            self._find_files_in_directory(self.test_files_dir, category, formats, test_files)
        
        return test_files
    
    def _find_files_in_directory(self, 
                                 directory,  #: str
                                 category: str, 
                                formats: List[str], 
                                test_files: Dict[str, List[Dict[str, Any]]]
                                ):
        """Find test files in a specific directory."""
        directory = self.Path(directory)
        if not directory.exists or not directory.is_dir():
            return
        
        for file_path in directory.iterdir():
            if file_path.is_file():
                filename = file_path.name
                ext = file_path.suffix.lower().lstrip('.')
                filepath = str(file_path)
                
                if ext in formats:
                    # Look for ground truth
                    ground_truth = self._find_ground_truth(filename, filepath)
                    if ground_truth:
                        test_files[category].append({
                            'file_name': filename,
                            'file_path': filepath,
                            'format': ext,
                            'reference_text': ground_truth,
                            'category': category
                        })
    
    def _find_ground_truth(self, filename: str, filepath: str) -> Optional[str]:
        """Find ground truth text for a test file."""
        base_name = os.path.splitext(filename)[0]
        ground_truth_variations = [
            f"{base_name}.txt",
            f"{base_name}.ground_truth.txt",
            f"{base_name}_reference.txt",
            f"{base_name}_gt.txt"
        ]
        
        # Check all possible ground truth locations
        for gt_dir in self.ground_truth_dirs:
            if gt_dir.exists():
                for gt_name in ground_truth_variations:
                    gt_path = gt_dir / gt_name
                    if gt_path.exists():
                        try:
                            with gt_path.open('r', encoding='utf-8') as f:
                                return f.read()
                        except Exception as e:
                            print(f"Warning: Could not read ground truth file {gt_path}: {e}")
            
        return None


# =============================================================================
# MAIN TEST CLASS
# =============================================================================

class TextQualityTest(unittest.TestCase):
    """Test case for text quality evaluation using BLEU, ROUGE-L, and structural metrics."""
    
    def setUp(self):
        """Set up test case with necessary data structures."""
        # Quality threshold from TESTING.md
        self.quality_threshold = 0.9
        
        # Weighting parameters from TESTING.md
        self.weights = {
            'text': {'alpha': 0.5, 'beta': 0.3, 'gamma': 0.2},
            'image': {'alpha': 0.6, 'beta': 0.4},
            'audio': {'alpha': 0.6, 'beta': 0.4},
            'video': {'alpha': 0.6, 'beta': 0.4},
            'application': {'alpha': 0.5, 'beta': 0.3, 'gamma': 0.2}
        }
        
        # Initialize test data manager
        self.data_manager = TestDataManager()
        
        # Find test files
        self.test_files = self.data_manager.find_test_files()
        
        # Create temp directory for output
        self.temp_output_dir = tempfile.mkdtemp()
        
        # Initialize validator
        self.validator = make_validator()
        
        # Results structure
        self.results = {
            'test_name': 'Text Quality for LLM Training',
            'timestamp': datetime.now().isoformat(),
            'quality_threshold': self.quality_threshold,
            'weights': self.weights,
            'categories': {},
            'overall': {
                'average_quality_score': 0,
                'meets_requirement': False
            }
        }
        
        # Metric functions (composable)
        self.bleu_scorer = calculate_bleu_score
        self.corpus_bleu_scorer = calculate_corpus_bleu_score
        self.rouge_scorer = calculate_rouge_l_score
        self.structural_scorer = calculate_structural_preservation_score
        self.quality_factor_calculator = calculate_text_quality_factor
    
    def _extract_text(self, file_data: Dict[str, Any]) -> str:
        """Extract text from a file using the processing pipeline."""
        file_path = file_data['file_path']
        
        try:
            # Create output path
            output_path = os.path.join(
                self.temp_output_dir,
                f"extracted_{os.path.basename(file_path)}.txt"
            )
            
            # Process file
            result = processing_pipeline.process_file(
                file_path,
                output_path,
                {'format': 'txt'}
            )
            
            # Read extracted text
            if result.success and os.path.exists(output_path):
                with open(output_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print(f"Warning: Processing failed for {file_path}")
                return ""
                
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _calculate_metrics(self, reference: str, extracted: str, category: str) -> Dict[str, float]:
        """Calculate all quality metrics for a text pair."""
        metrics = {}
        
        # Calculate BLEU score
        metrics['bleu'] = self.bleu_scorer(reference, extracted)
        
        # Calculate ROUGE-L score (F1)
        rouge_scores = self.rouge_scorer(reference, extracted)
        metrics['rouge_l'] = rouge_scores['f1']
        
        # Calculate structural preservation for text and application categories
        if category in ['text', 'application']:
            metrics['structural'] = self.structural_scorer(reference, extracted)
        
        return metrics
    
    def test_text_quality(self):
        """Main test method that evaluates text quality across all categories."""
        total_files = 0
        total_quality_score = 0
        
        # Process each category
        for category, files in self.test_files.items():
            if not files:
                print(f"\nNo test files found for category: {category}")
                continue
                
            print(f"\n{'='*60}")
            print(f"Testing {category.upper()} files")
            print(f"{'='*60}")
            
            category_files = 0
            category_quality_score = 0
            category_results = []
            
            # Get weights for this category
            weights = self.weights[category]
            
            # Process each file
            for file_data in files:
                print(f"\nProcessing: {file_data['file_name']}")
                
                # Extract text
                extracted_text = self._extract_text(file_data)
                reference_text = file_data['reference_text']
                
                # Calculate metrics
                metrics = self._calculate_metrics(reference_text, extracted_text, category)
                
                # Calculate quality factor
                if category in ['text', 'application']:
                    quality_factor = self.quality_factor_calculator(
                        metrics['bleu'],
                        metrics['rouge_l'],
                        metrics['structural'],
                        weights['alpha'],
                        weights['beta'],
                        weights['gamma']
                    )
                else:
                    quality_factor = self.quality_factor_calculator(
                        metrics['bleu'],
                        metrics['rouge_l'],
                        None,
                        weights['alpha'],
                        weights['beta']
                    )
                
                # Determine if meets threshold
                meets_threshold = quality_factor >= self.quality_threshold
                
                # Store results
                file_result = {
                    'file_name': file_data['file_name'],
                    'format': file_data['format'],
                    'metrics': metrics,
                    'quality_factor': quality_factor,
                    'meets_threshold': meets_threshold,
                    'reference_length': len(reference_text),
                    'extracted_length': len(extracted_text)
                }
                category_results.append(file_result)
                
                # Update statistics
                category_files += 1
                category_quality_score += quality_factor
                total_files += 1
                total_quality_score += quality_factor
                
                # Print results
                print(f"  BLEU Score: {metrics['bleu']:.4f}")
                print(f"  ROUGE-L F1: {metrics['rouge_l']:.4f}")
                if 'structural' in metrics:
                    print(f"  Structural: {metrics['structural']:.4f}")
                print(f"  Quality Factor: {quality_factor:.4f}")
                print(f"  Meets Threshold: {'✓' if meets_threshold else '✗'}")
            
            # Calculate category average
            if category_files > 0:
                category_avg_quality = category_quality_score / category_files
                category_meets_threshold = category_avg_quality >= self.quality_threshold
                
                # Store category results
                self.results['categories'][category] = {
                    'files_tested': category_files,
                    'average_quality_score': category_avg_quality,
                    'meets_threshold': category_meets_threshold,
                    'file_results': category_results
                }
                
                # Print category summary
                print(f"\n{category.upper()} Summary:")
                print(f"  Files tested: {category_files}")
                print(f"  Average quality: {category_avg_quality:.4f}")
                print(f"  Meets threshold: {'✓' if category_meets_threshold else '✗'}")
        
        # Calculate overall results
        if total_files > 0:
            overall_avg_quality = total_quality_score / total_files
            overall_meets_threshold = overall_avg_quality >= self.quality_threshold
            
            self.results['overall'] = {
                'total_files_tested': total_files,
                'average_quality_score': overall_avg_quality,
                'meets_threshold': overall_meets_threshold
            }
            
            # Print overall summary
            print(f"\n{'='*60}")
            print("OVERALL RESULTS")
            print(f"{'='*60}")
            print(f"Total files tested: {total_files}")
            print(f"Average quality score: {overall_avg_quality:.4f}")
            print(f"Meets threshold (≥{self.quality_threshold}): {'✓' if overall_meets_threshold else '✗'}")
            
            # Assert requirement is met
            self.assertGreaterEqual(
                overall_avg_quality,
                self.quality_threshold,
                f"Overall text quality ({overall_avg_quality:.4f}) must be at least {self.quality_threshold}"
            )
        else:
            self.results['overall'] = {
                'total_files_tested': 0,
                'average_quality_score': 0,
                'meets_threshold': False
            }
            self.fail("No test files found with ground truth")
    
    def tearDown(self):
        """Clean up and save results."""
        # Save results to JSON
        os.makedirs('tests/collected_results', exist_ok=True)
        output_file = os.path.join('tests/collected_results', 'text_quality.json')
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to: {output_file}")
        
        # Save results to Markdown
        markdown_file = os.path.join('tests/collected_results', 'latest_test_results.md')
        self._save_results_to_markdown(markdown_file)
        print(f"Results also saved to: {markdown_file}")
        
        # Clean up temp directory
        if os.path.exists(self.temp_output_dir):
            import shutil
            shutil.rmtree(self.temp_output_dir)

    def _save_results_to_markdown(self, filepath: str):
        """Save test results to a markdown file."""
        with open(filepath, 'w') as f:
            f.write("# Text Quality Test Results\n\n")
            f.write(f"**Test Name:** {self.results['test_name']}\n")
            f.write(f"**Timestamp:** {self.results['timestamp']}\n")
            f.write(f"**Quality Threshold:** {self.results['quality_threshold']}\n\n")
            
            # Overall Results
            f.write("## Overall Results\n\n")
            overall = self.results['overall']
            f.write(f"- **Total Files Tested:** {overall.get('total_files_tested', 0)}\n")
            f.write(f"- **Average Quality Score:** {overall['average_quality_score']:.4f}\n")
            f.write(f"- **Meets Threshold:** {'✅ Yes' if overall['meets_threshold'] else '❌ No'}\n\n")
            
            # Category Results
            f.write("## Results by Category\n\n")
            for category, data in self.results['categories'].items():
                f.write(f"### {category.title()}\n")
                f.write(f"- **Files Tested:** {data['files_tested']}\n")
                f.write(f"- **Average Quality Score:** {data['average_quality_score']:.4f}\n")
                f.write(f"- **Meets Threshold:** {'✅ Yes' if data['meets_threshold'] else '❌ No'}\n\n")
                
                # File Details
                if data.get('file_results'):
                    f.write("#### File Details\n\n")
                    f.write("| File | Format | BLEU | ROUGE-L | Structural | Quality Factor | Meets Threshold |\n")
                    f.write("|------|--------|------|---------|------------|----------------|------------------|\n")
                    
                    for file_result in data['file_results']:
                        metrics = file_result['metrics']
                        structural = f"{metrics.get('structural', 0):.4f}" if 'structural' in metrics else "N/A"
                        threshold_icon = "✅" if file_result['meets_threshold'] else "❌"
                        
                        f.write(f"| {file_result['file_name']} | {file_result['format']} | "
                               f"{metrics['bleu']:.4f} | {metrics['rouge_l']:.4f} | {structural} | "
                               f"{file_result['quality_factor']:.4f} | {threshold_icon} |\n")
                    f.write("\n")
            
            # Weights Configuration
            f.write("## Weights Configuration\n\n")
            for category, weights in self.results['weights'].items():
                f.write(f"**{category.title()}:**\n")
                for weight_name, weight_value in weights.items():
                    f.write(f"- {weight_name}: {weight_value}\n")
                f.write("\n")


if __name__ == '__main__':
    unittest.main()