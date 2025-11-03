"""
Views for reports app.
"""

from datetime import datetime, date
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from apps.reports.services import ReportService, AnalyticsService
from apps.reports.exporters import ExcelExporter, PDFExporter, ExportService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary_report(request):
    """
    Get summary report for the user.
    
    Query params:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Convert string dates to date objects
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    report = ReportService.get_summary_report(request.user, start_date, end_date)
    
    return Response({
        'total_income': float(report.total_income),
        'total_expense': float(report.total_expense),
        'net_balance': float(report.net_balance),
        'transaction_count': report.transaction_count,
        'period_start': report.period_start.isoformat(),
        'period_end': report.period_end.isoformat(),
        'details': report.details
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_report(request):
    """
    Get monthly report.
    
    Query params:
        - year: Year (default: current year)
        - month: Month (default: current month)
    """
    year = int(request.query_params.get('year', datetime.now().year))
    month = int(request.query_params.get('month', datetime.now().month))
    
    report = ReportService.get_monthly_report(request.user, year, month)
    
    return Response({
        'total_income': float(report.total_income),
        'total_expense': float(report.total_expense),
        'net_balance': float(report.net_balance),
        'transaction_count': report.transaction_count,
        'period_start': report.period_start.isoformat(),
        'period_end': report.period_end.isoformat(),
        'details': report.details
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_wise_report(request):
    """
    Get category-wise breakdown report.
    
    Query params:
        - type: Transaction type ('INCOME' or 'EXPENSE')
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
    """
    transaction_type = request.query_params.get('type', 'EXPENSE').upper()
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Convert string dates to date objects
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    categories = ReportService.get_category_wise_report(
        request.user, transaction_type, start_date, end_date
    )
    
    return Response({
        'transaction_type': transaction_type,
        'categories': [
            {
                'category_name': cat.category_name,
                'category_id': cat.category_id,
                'total_amount': float(cat.total_amount),
                'transaction_count': cat.transaction_count,
                'percentage': float(cat.percentage),
                'color': cat.color
            }
            for cat in categories
        ]
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trend_analysis(request):
    """
    Get trend analysis for the last N months.
    
    Query params:
        - months: Number of months (default: 6)
    """
    months = int(request.query_params.get('months', 6))
    
    trends = ReportService.get_trend_analysis(request.user, months)
    
    return Response(trends)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_expenses(request):
    """
    Get top expenses.
    
    Query params:
        - limit: Number of expenses (default: 10)
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
    """
    limit = int(request.query_params.get('limit', 10))
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Convert string dates to date objects
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    expenses = ReportService.get_top_expenses(
        request.user, start_date, end_date, limit
    )
    
    return Response({'top_expenses': expenses})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def budget_analysis(request):
    """
    Get budget analysis.
    
    Query params:
        - month: Month (default: current month)
        - year: Year (default: current year)
    """
    month = int(request.query_params.get('month', datetime.now().month))
    year = int(request.query_params.get('year', datetime.now().year))
    
    analysis = ReportService.get_budget_analysis(request.user, month, year)
    
    return Response({'budget_analysis': analysis})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spending_patterns(request):
    """
    Get spending pattern analysis.
    
    Query params:
        - months: Number of months (default: 12)
    """
    months = int(request.query_params.get('months', 12))
    
    patterns = AnalyticsService.get_spending_patterns(request.user, months)
    
    return Response(patterns)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_excel(request):
    """
    Export report to Excel.
    
    Request body:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
    """
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    
    # Convert string dates to date objects
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Create export service with Excel strategy
    export_service = ExportService(ExcelExporter())
    
    try:
        file_content, content_type, filename = export_service.export_report(
            request.user, 'summary', start_date, end_date
        )
        
        # Create HTTP response with file
        response = HttpResponse(
            file_content.read(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_pdf(request):
    """
    Export report to PDF.
    
    Request body:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
    """
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    
    # Convert string dates to date objects
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Create export service with PDF strategy
    export_service = ExportService(PDFExporter())
    
    try:
        file_content, content_type, filename = export_service.export_report(
            request.user, 'summary', start_date, end_date
        )
        
        # Create HTTP response with file
        response = HttpResponse(
            file_content.read(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

