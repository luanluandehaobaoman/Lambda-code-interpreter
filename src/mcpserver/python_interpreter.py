import sys
import io
import contextlib
import subprocess
import importlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP(name="PythonInterpreter", stateless_http=True)

class SecurityError(Exception):
    """安全相关异常"""
    pass

class DependencyManager:
    """依赖包管理器"""
    
    def __init__(self):
        # 预装的数据科学包
        self.preinstalled = {
            'pandas', 'numpy', 'matplotlib', 'scipy', 
            'sklearn', 'seaborn', 'requests', 'fastapi',
            'pydantic', 'uvicorn', 'json', 'os', 're',
            'datetime', 'math', 'random', 'collections'
        }
        
        self.tmp_dir = Path("/tmp/py_packages")
        self.tmp_dir.mkdir(exist_ok=True)
        self.installed_packages = set()
    
    def resolve_dependencies(self, requirements: List[str]) -> Dict[str, List[str]]:
        """解析依赖需求"""
        result = {
            "ready": [],      # 已就绪的包
            "installing": []  # 需要安装的包
        }
        
        for pkg in requirements:
            if pkg in self.preinstalled:
                result["ready"].append(pkg)
            else:
                result["installing"].append(pkg)
        
        return result
    
    def install_package(self, package_name: str) -> Dict[str, Any]:
        """安装单个包"""
        if package_name in self.installed_packages:
            return {"success": True, "message": f"Package {package_name} already installed"}
        
        try:
            # 尝试安装到临时目录
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "--target", str(self.tmp_dir), 
                "--no-deps",  # 不安装依赖，避免复杂性
                package_name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 添加到Python路径
                if str(self.tmp_dir) not in sys.path:
                    sys.path.insert(0, str(self.tmp_dir))
                
                self.installed_packages.add(package_name)
                return {"success": True, "message": f"Successfully installed {package_name}"}
            else:
                return {
                    "success": False, 
                    "message": f"Failed to install {package_name}: {result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False, 
                "message": f"Installation of {package_name} timed out"
            }
        except Exception as e:
            return {
                "success": False, 
                "message": f"Error installing {package_name}: {str(e)}"
            }
    
    def setup_environment(self, requirements: List[str]) -> Dict[str, Any]:
        """设置执行环境"""
        if not requirements:
            return {"status": "success"}
        
        deps = self.resolve_dependencies(requirements)
        warnings = []
        
        # 安装需要安装的包
        for pkg in deps["installing"]:
            result = self.install_package(pkg)
            if not result["success"]:
                warnings.append(f"Failed to install {pkg}: {result['message']}")
        
        if warnings:
            return {"warnings": "; ".join(warnings)}
        
        return {"status": "success"}

class PythonInterpreter:
    """Python代码解释器"""
    
    def __init__(self):
        self.dependency_manager = DependencyManager()
        # 阻止的危险操作模式
        self.blocked_patterns = [
            'os.system', 'subprocess.call', 'subprocess.run',
            'subprocess.Popen', '__import__("os")', '__import__("subprocess")'
        ]
    
    def safe_exec(self, code: str, namespace: Dict[str, Any]) -> None:
        """安全执行代码"""
        # 基础安全检查
        for pattern in self.blocked_patterns:
            if pattern in code:
                raise SecurityError(f"Blocked dangerous operation: {pattern}")
        
        # 执行代码（依赖Lambda沙箱保护）
        exec(code, namespace)
    
    def execute_code(self, code: str, requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """执行Python代码"""
        warnings = []
        
        try:
            # 处理依赖
            if requirements:
                deps_result = self.dependency_manager.setup_environment(requirements)
                if "warnings" in deps_result:
                    warnings.append(deps_result["warnings"])
            
            # 捕获输出
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            # 创建执行命名空间
            namespace = {
                "__name__": "__main__",
                "__builtins__": __builtins__
            }
            
            with contextlib.redirect_stdout(stdout_buffer), \
                 contextlib.redirect_stderr(stderr_buffer):
                
                # 安全执行代码
                self.safe_exec(code, namespace)
            
            # 获取结果
            result_value = namespace.get("result", "")
            if result_value == "" and stdout_buffer.getvalue():
                result_value = "Code executed successfully"
            
            return {
                "success": True,
                "result": str(result_value),
                "stdout": stdout_buffer.getvalue(),
                "stderr": stderr_buffer.getvalue(),
                "warnings": "; ".join(warnings) if warnings else ""
            }
            
        except SecurityError as e:
            return {
                "success": False,
                "result": f"Security Error: {str(e)}",
                "stdout": "",
                "stderr": str(e),
                "warnings": "; ".join(warnings) if warnings else ""
            }
        except Exception as e:
            return {
                "success": False,
                "result": f"Execution Error: {str(e)}",
                "stdout": "",
                "stderr": str(e),
                "warnings": "; ".join(warnings) if warnings else ""
            }

# 创建解释器实例
interpreter = PythonInterpreter()

@mcp.tool(description="Execute Python code and return the result")
def execute_python(code: str, requirements: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    执行Python代码并返回结果
    
    Args:
        code: 要执行的Python代码
        requirements: 需要安装的Python包列表（可选）
    
    Returns:
        {
            "success": bool,
            "result": str,  # 执行结果或错误信息
            "stdout": str,  # 标准输出
            "stderr": str,  # 标准错误
            "warnings": str # 依赖包警告信息
        }
    """
    return interpreter.execute_code(code, requirements)

@mcp.tool(description="List available preinstalled packages")
def list_preinstalled_packages() -> Dict[str, Any]:
    """
    列出预装的Python包
    
    Returns:
        {
            "packages": List[str]  # 预装包列表
        }
    """
    return {
        "packages": sorted(list(interpreter.dependency_manager.preinstalled))
    }

@mcp.tool(description="Get Python environment information")
def get_environment_info() -> Dict[str, Any]:
    """
    获取Python环境信息
    
    Returns:
        {
            "python_version": str,
            "platform": str,
            "available_memory": str,
            "temp_dir": str
        }
    """
    import platform
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "temp_dir": str(interpreter.dependency_manager.tmp_dir),
        "installed_packages": sorted(list(interpreter.dependency_manager.installed_packages))
    }