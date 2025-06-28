#!/usr/bin/env python3
"""
Test Results Reporter
Test sonuçlarını kaydet ve raporla
"""

import json
import time
import datetime
from pathlib import Path
from typing import Dict, List, Any
import subprocess
import sys


class TestReporter:
    """Test sonuçlarını kaydet ve raporla"""

    def __init__(self, output_dir: str = "test_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def run_tests_with_coverage(self) -> Dict[str, Any]:
        """Tüm testleri coverage ile çalıştır"""
        results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "modules": {},
            "summary": {"total_tests": 0, "passed": 0, "failed": 0, "coverage": {}},
        }

        # Test modülleri
        test_modules = [
            ("obstacle_avoidance", "tests/test_obstacle_avoidance.py"),
            ("kalman_odometry", "tests/test_kalman_odometry.py"),
            ("motor_controller", "tests/test_motor_controller.py"),
            ("path_planner", "tests/test_path_planner.py"),
        ]

        for module_name, test_file in test_modules:
            print(f"🧪 {module_name} testleri çalıştırılıyor...")
            module_result = self._run_single_module(module_name, test_file)
            results["modules"][module_name] = module_result

            # Summary güncelle
            results["summary"]["total_tests"] += module_result["total"]
            results["summary"]["passed"] += module_result["passed"]
            results["summary"]["failed"] += module_result["failed"]

        # Toplam başarı oranı
        total = results["summary"]["total_tests"]
        passed = results["summary"]["passed"]
        results["summary"]["success_rate"] = (passed / total * 100) if total > 0 else 0

        return results

    def _run_single_module(self, module_name: str, test_file: str) -> Dict[str, Any]:
        """Tek modül testini çalıştır"""
        try:
            # pytest ile JSON output
            cmd = [
                "python3",
                "-m",
                "pytest",
                test_file,
                "--json-report",
                f"--json-report-file={self.output_dir}/{module_name}_report.json",
                "--cov=src",
                f"--cov-report=html:{self.output_dir}/{module_name}_coverage",
                f"--cov-report=json:{self.output_dir}/{module_name}_coverage.json",
                "-v",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

            # JSON raporu oku
            json_file = self.output_dir / f"{module_name}_report.json"
            if json_file.exists():
                with open(json_file) as f:
                    pytest_data = json.load(f)

                return {
                    "status": "PASS" if result.returncode == 0 else "FAIL",
                    "total": pytest_data.get("summary", {}).get("total", 0),
                    "passed": pytest_data.get("summary", {}).get("passed", 0),
                    "failed": pytest_data.get("summary", {}).get("failed", 0),
                    "duration": pytest_data.get("duration", 0),
                    "coverage_file": f"{module_name}_coverage.json",
                }
            else:
                # Fallback - basit regex parse
                return self._parse_output(result.stdout, result.returncode)

        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "total": 0,
                "passed": 0,
                "failed": 0,
            }

    def _parse_output(self, output: str, return_code: int) -> Dict[str, Any]:
        """Test çıktısını parse et"""
        lines = output.split("\n")

        # Son satırda sonuçları ara
        for line in reversed(lines):
            if "passed" in line or "failed" in line:
                # "22 passed in 1.43s" format
                import re

                match = re.search(r"(\d+) passed", line)
                passed = int(match.group(1)) if match else 0

                match = re.search(r"(\d+) failed", line)
                failed = int(match.group(1)) if match else 0

                return {
                    "status": "PASS" if return_code == 0 else "FAIL",
                    "total": passed + failed,
                    "passed": passed,
                    "failed": failed,
                    "duration": 0,
                }

        return {"status": "ERROR", "total": 0, "passed": 0, "failed": 0}

    def save_results(self, results: Dict[str, Any]):
        """Sonuçları kaydet"""
        # JSON formatında kaydet
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = self.output_dir / f"test_results_{timestamp}.json"

        with open(json_file, "w") as f:
            json.dump(results, f, indent=2)

        # En son sonuçları da kaydet
        latest_file = self.output_dir / "latest_results.json"
        with open(latest_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"📊 Test sonuçları kaydedildi: {json_file}")

        # HTML raporu oluştur
        self._generate_html_report(results)

    def _generate_html_report(self, results: Dict[str, Any]):
        """HTML raporu oluştur"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OT-BICME Test Raporu</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .module {{ margin: 20px 0; padding: 15px; border: 1px solid #bdc3c7; border-radius: 5px; }}
        .pass {{ background: #d5eda6; }}
        .fail {{ background: #f2d7d5; }}
        .success-rate {{ font-size: 24px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 OT-BICME Test Raporu</h1>
        <p>Oluşturulma: {results['timestamp']}</p>
    </div>

    <div class="summary">
        <h2>📊 Özet</h2>
        <div class="success-rate">Başarı Oranı: {results['summary']['success_rate']:.1f}%</div>
        <p>Toplam Test: {results['summary']['total_tests']}</p>
        <p>✅ Başarılı: {results['summary']['passed']}</p>
        <p>❌ Başarısız: {results['summary']['failed']}</p>
    </div>

    <h2>🔍 Modül Detayları</h2>
    <table>
        <tr>
            <th>Modül</th>
            <th>Durum</th>
            <th>Toplam</th>
            <th>Başarılı</th>
            <th>Başarısız</th>
            <th>Başarı Oranı</th>
        </tr>
"""

        for module_name, module_data in results["modules"].items():
            total = module_data.get("total", 0)
            passed = module_data.get("passed", 0)
            success_rate = (passed / total * 100) if total > 0 else 0
            status_class = "pass" if module_data.get("status") == "PASS" else "fail"

            html_content += f"""
        <tr class="{status_class}">
            <td>{module_name}</td>
            <td>{module_data.get('status', 'UNKNOWN')}</td>
            <td>{total}</td>
            <td>{passed}</td>
            <td>{module_data.get('failed', 0)}</td>
            <td>{success_rate:.1f}%</td>
        </tr>
"""

        html_content += """
    </table>

    <div style="margin-top: 40px; text-align: center; color: #7f8c8d;">
        <p>🔧 Hacı Abi Test Framework tarafından oluşturuldu</p>
    </div>
</body>
</html>
"""

        html_file = self.output_dir / "test_report.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"📋 HTML raporu oluşturuldu: {html_file}")


def main():
    """Ana fonksiyon"""
    print("🚀 OT-BICME Test Suite Başlatılıyor...")
    print("=" * 60)

    reporter = TestReporter()
    results = reporter.run_tests_with_coverage()
    reporter.save_results(results)

    print("=" * 60)
    print(f"✅ Başarılı: {results['summary']['passed']}")
    print(f"❌ Başarısız: {results['summary']['failed']}")
    print(f"📊 Başarı Oranı: {results['summary']['success_rate']:.1f}%")

    if results["summary"]["success_rate"] >= 90:
        print("🎉 Mükemmel! Test başarı oranı %90'ın üstünde!")
        sys.exit(0)
    elif results["summary"]["success_rate"] >= 75:
        print("👍 İyi! Test başarı oranı %75'in üstünde.")
        sys.exit(0)
    else:
        print("⚠️  Test başarı oranı düşük. Daha fazla çalışma gerek.")
        sys.exit(1)


if __name__ == "__main__":
    main()
