from services import CodeExtractorService
from services import CodeReportService
from core import PythonASTParser, FileWriter, ImportAnalyzer, DependencyResolver, ImportOptimizer


def create_extractor() -> CodeExtractorService:
    """
    Factory function to create a configured extractor service.
    
    This is like a recipe that assembles all the ingredients (components)
    in the right way to create the final dish (working extractor).
    """
    parser = PythonASTParser()
    file_writer = FileWriter()
    import_analyzer = ImportAnalyzer()
    dependency_resolver = DependencyResolver()
    import_optimizer = ImportOptimizer()
    return CodeExtractorService(parser, file_writer, import_analyzer, dependency_resolver, import_optimizer)

def create_report_service() -> CodeReportService:
    """
    Factory function to create a configured report service.
    
    Like assembling a data analysis toolkit - gives you everything needed
    to generate insightful reports about your codebase structure.
    """
    parser = PythonASTParser()
    dependency_resolver = DependencyResolver()
    return CodeReportService(parser, dependency_resolver)