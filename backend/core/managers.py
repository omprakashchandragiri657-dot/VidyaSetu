from django.db import models


class TenantManager(models.Manager):
    """Custom manager for multi-tenant models"""
    
    def get_queryset(self):
        """Override to filter by current tenant (college)"""
        # This will be enhanced with middleware to get current college
        return super().get_queryset()
    
    def for_tenant(self, college):
        """Filter queryset by specific college"""
        return self.get_queryset().filter(college=college)


class AchievementManager(models.Manager):
    """Custom manager for achievements with tenant filtering"""
    
    def get_queryset(self):
        """Override to filter by current tenant (college)"""
        return super().get_queryset()
    
    def for_tenant(self, college):
        """Filter achievements by college through student's user"""
        return self.get_queryset().filter(student__user__college=college)
    
    def pending_for_tenant(self, college):
        """Get pending achievements for a specific college"""
        return self.for_tenant(college).filter(status='pending')
    
    def approved_for_tenant(self, college):
        """Get approved achievements for a specific college"""
        return self.for_tenant(college).filter(status='approved')
