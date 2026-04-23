from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    """Только учитель (is_staff=True) имеет доступ."""
    message = "Доступ разрешён только учителям."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsStudent(BasePermission):
    """Только ученик (is_staff=False) имеет доступ."""
    message = "Доступ разрешён только ученикам."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_staff)


class IsTeacherOrReadOwn(BasePermission):
    """Учитель видит всё. Ученик видит только своё."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # obj — это Submission, у которого есть поле user
        return obj.user == request.user