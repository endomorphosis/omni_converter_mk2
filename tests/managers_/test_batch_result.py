# """
# Test the batch result module.
# """

# import unittest
# from datetime import datetime, timedelta

# from core.processing_pipeline.processing_result import ProcessingResult
# from monitors.batch_result import BatchResult


# class TestBatchResult(unittest.TestCase):
#     """Test the BatchResult class."""
    
#     def setUp(self):
#         """Set up test fixtures."""
#         # Create sample processing results
#         self.success_result = ProcessingResult(
#             success=True,
#             file_path="/path/to/success.txt",
#             output_path="/path/to/output/success.txt",
#             format="txt",
#             metadata={"key": "value"}
#         )
        
#         self.failure_result = ProcessingResult(
#             success=False,
#             file_path="/path/to/failure.txt",
#             output_path="/path/to/output/failure.txt",
#             format="txt",
#             errors=["Error message"]
#         )
    
#     def test_init_with_defaults(self):
#         """Test initialization with default values."""
#         batch_result = BatchResult()
        
#         self.assertEqual(batch_result.total_files, 0)
#         self.assertEqual(batch_result.successful_files, 0)
#         self.assertEqual(batch_result.failed_files, 0)
#         self.assertEqual(len(batch_result.results), 0)
#         self.assertEqual(len(batch_result.statistics), 0)
#         self.assertIsNotNone(batch_result.start_time)
#         self.assertIsNone(batch_result.end_time)
    
#     def test_init_with_results(self):
#         """Test initialization with results."""
#         results = [self.success_result, self.failure_result]
#         batch_result = BatchResult(results=results)
        
#         self.assertEqual(batch_result.total_files, 2)
#         self.assertEqual(batch_result.successful_files, 1)
#         self.assertEqual(batch_result.failed_files, 1)
#         self.assertEqual(len(batch_result.results), 2)
    
#     def test_add_result(self):
#         """Test adding results."""
#         batch_result = BatchResult()
        
#         # Add success result
#         batch_result.add_result(self.success_result)
#         self.assertEqual(batch_result.total_files, 1)
#         self.assertEqual(batch_result.successful_files, 1)
#         self.assertEqual(batch_result.failed_files, 0)
        
#         # Add failure result
#         batch_result.add_result(self.failure_result)
#         self.assertEqual(batch_result.total_files, 2)
#         self.assertEqual(batch_result.successful_files, 1)
#         self.assertEqual(batch_result.failed_files, 1)
    
#     def test_complete(self):
#         """Test completion of batch processing."""
#         batch_result = BatchResult()
#         batch_result.add_result(self.success_result)
        
#         # Complete batch processing
#         batch_result.complete()
        
#         self.assertIsNotNone(batch_result.end_time)
#         self.assertIn('duration_seconds', batch_result.statistics)
#         self.assertIn('success_rate', batch_result.statistics)
#         self.assertEqual(batch_result.statistics['success_rate'], 100.0)
    
#     def test_get_summary(self):
#         """Test getting summary."""
#         batch_result = BatchResult()
#         batch_result.add_result(self.success_result)
#         batch_result.add_result(self.failure_result)
#         batch_result.complete()
        
#         summary = batch_result.get_summary()
        
#         self.assertEqual(summary['total_files'], 2)
#         self.assertEqual(summary['successful_files'], 1)
#         self.assertEqual(summary['failed_files'], 1)
#         self.assertEqual(summary['success_rate_percent'], 50.0)
#         self.assertIn('duration_seconds', summary)
#         self.assertIn('start_time', summary)
#         self.assertIn('end_time', summary)
    
#     def test_get_failed_files(self):
#         """Test getting failed files."""
#         batch_result = BatchResult()
#         batch_result.add_result(self.success_result)
#         batch_result.add_result(self.failure_result)
        
#         failed_files = batch_result.get_failed_files()
        
#         self.assertEqual(len(failed_files), 1)
#         self.assertEqual(failed_files[0], self.failure_result.file_path)
    
#     def test_get_successful_files(self):
#         """Test getting successful files."""
#         batch_result = BatchResult()
#         batch_result.add_result(self.success_result)
#         batch_result.add_result(self.failure_result)
        
#         successful_files = batch_result.get_successful_files()
        
#         self.assertEqual(len(successful_files), 1)
#         self.assertEqual(successful_files[0], self.success_result.file_path)
    
#     def test_to_dict(self):
#         """Test conversion to dictionary."""
#         batch_result = BatchResult()
#         batch_result.add_result(self.success_result)
#         batch_result.complete()
        
#         result_dict = batch_result.to_dict()
        
#         self.assertEqual(result_dict['total_files'], 1)
#         self.assertEqual(result_dict['successful_files'], 1)
#         self.assertEqual(result_dict['failed_files'], 0)
#         self.assertEqual(len(result_dict['results']), 1)
#         self.assertIn('start_time', result_dict)
#         self.assertIn('end_time', result_dict)
    
#     def test_str_representation(self):
#         """Test string representation."""
#         batch_result = BatchResult()
#         batch_result.add_result(self.success_result)
#         batch_result.add_result(self.failure_result)
        
#         str_repr = str(batch_result)
        
#         self.assertIn("Batch Processing Result", str_repr)
#         self.assertIn("Total Files: 2", str_repr)
#         self.assertIn("Successful: 1", str_repr)
#         self.assertIn("Failed: 1", str_repr)


# if __name__ == "__main__":
#     unittest.main()