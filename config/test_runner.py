from django.test.runner import DiscoverRunner


class DefaultAppDiscoverRunner(DiscoverRunner):
    default_test_labels = ["tasks"]

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        return super().build_suite(
            test_labels or self.default_test_labels,
            extra_tests=extra_tests,
            **kwargs,
        )
