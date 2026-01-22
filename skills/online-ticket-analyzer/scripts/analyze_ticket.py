#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
线上工单分析主入口脚本
协调所有阶段：阶段0（首次使用检查）、阶段1（准备与指令生成）、阶段2（综合分析）
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

# 导入各个模块
from utils import generate_ticket_id
from phase0_init import init_phase_0
from parse_input import parse_user_input, extract_ticket_info, extract_time_range
from phase1_prepare import init_phase_1
from mcp_handler import generate_mcp_instructions
from phase2_analyze import init_phase_2


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='线上工单分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础分析
  python analyze_ticket.py --description "用户反馈登录接口返回500错误" --project-path "."

  # 带图片分析
  python analyze_ticket.py --description "用户反馈支付失败" --image "error.png" --project-path "."

  # 指定时间范围
  python analyze_ticket.py --description "用户反馈登录接口返回500错误" \\
    --start-time "2025-01-20 10:00:00" --end-time "2025-01-20 11:00:00" \\
    --project-path "."
        """
    )
    
    # 输入参数
    input_group = parser.add_argument_group('输入参数')
    input_group.add_argument(
        '--description',
        type=str,
        help='问题描述文字'
    )
    input_group.add_argument(
        '--file',
        type=str,
        help='包含问题描述的文件路径'
    )
    input_group.add_argument(
        '--image',
        type=str,
        help='问题相关图片路径（支持OCR识别）'
    )
    
    # 项目参数
    project_group = parser.add_argument_group('项目参数')
    project_group.add_argument(
        '--project-path',
        type=str,
        default='.',
        help='项目根目录路径（默认: 当前目录）'
    )
    project_group.add_argument(
        '--service',
        type=str,
        help='指定服务名称（如果不提供则分析所有服务）'
    )
    
    # 时间参数
    time_group = parser.add_argument_group('时间参数')
    time_group.add_argument(
        '--start-time',
        type=str,
        help='查询开始时间（格式: YYYY-MM-DD HH:MM:SS）'
    )
    time_group.add_argument(
        '--end-time',
        type=str,
        help='查询结束时间（格式: YYYY-MM-DD HH:MM:SS）'
    )
    
    # 工单参数
    ticket_group = parser.add_argument_group('工单参数')
    ticket_group.add_argument(
        '--ticket-id',
        type=str,
        help='工单ID（如果不提供则自动生成）'
    )
    
    # 控制参数
    control_group = parser.add_argument_group('控制参数')
    control_group.add_argument(
        '--skip-phase0',
        action='store_true',
        help='跳过阶段0（首次使用检查）'
    )
    control_group.add_argument(
        '--skip-phase1',
        action='store_true',
        help='跳过阶段1（如果已有MCP结果）'
    )
    control_group.add_argument(
        '--skip-phase2',
        action='store_true',
        help='跳过阶段2（仅生成指令）'
    )
    control_group.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    # 验证输入参数
    if not args.description and not args.file and not args.image:
        parser.error("必须提供 --description、--file 或 --image 参数之一")
    
    # 解析用户输入
    print("="*60)
    print("🔍 线上工单分析工具")
    print("="*60)
    
    user_input_text = parse_user_input(
        description=args.description,
        image_path=args.image,
        file_path=args.file
    )
    
    if not user_input_text:
        print("❌ 无法解析用户输入", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"\n📝 用户输入: {user_input_text[:200]}...")
    
    # 提取工单信息
    print("\n📋 解析工单信息...")
    ticket_info = extract_ticket_info(user_input_text, project_path=args.project_path)
    
    # 如果命令行指定了服务，添加到工单信息中
    if args.service:
        if args.service not in ticket_info.get('services', []):
            ticket_info.setdefault('services', []).append(args.service)
    
    # 生成工单ID
    ticket_id = args.ticket_id or generate_ticket_id(
        user_input_text,
        ticket_info.get('ticket_id')
    )
    print(f"  ✅ 工单ID: {ticket_id}")
    
    if args.verbose:
        print(f"  - 服务: {ticket_info.get('services', [])}")
        print(f"  - 用户信息: {ticket_info.get('user_info', {})}")
        print(f"  - 接口信息: {ticket_info.get('api_info', {})}")
    
    # 计算时间范围
    print("\n⏰ 计算查询时间范围...")
    time_range = extract_time_range(
        ticket_info,
        start_time=args.start_time,
        end_time=args.end_time
    )
    start_time, end_time, time_source = time_range
    print(f"  ✅ 时间范围: {time_source}")
    if start_time and end_time:
        print(f"     {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查时间是否在未来
        now = datetime.now()
        if end_time > now + timedelta(hours=1):
            print(f"  ⚠️  注意：查询结束时间在未来（当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}）")
            print(f"     如果这是测试数据或系统时间设置不同，可以继续使用")
            print(f"     否则请检查时间是否正确")
    
    # 阶段0：首次使用检查
    if not args.skip_phase0:
        print("\n" + "="*60)
        print("📋 阶段0：首次使用检查")
        print("="*60)
        context_complete, config_complete = init_phase_0(args.project_path, skip_if_complete=False)
        
        # 如果配置不完整，给出明确提示
        if not context_complete or not config_complete:
            print("\n" + "="*60)
            print("⚠️  配置不完整，需要完成初始化")
            print("="*60)
            if not context_complete:
                print("\n❌ 项目上下文不完整")
                print("   请按照上述提示，让AI通读项目代码生成完整的项目上下文")
            if not config_complete:
                print("\n❌ SigNoz配置不完整")
                print("   请按照上述提示，让AI通读项目代码生成完整的SigNoz配置")
            print("\n💡 提示：完成配置生成后，重新运行此命令继续分析")
            sys.exit(1)
        else:
            print("\n✅ 阶段0检查完成，配置信息完整")
    else:
        print("\n⏭️  跳过阶段0（首次使用检查）")
    
    # 阶段1：准备与指令生成
    if not args.skip_phase1:
        ticket_context = init_phase_1(
            args.project_path,
            ticket_info,
            time_range,
            ticket_id
        )
        
        # 生成MCP调用指令
        print("\n📋 生成MCP调用指令...")
        # 注意：generate_mcp_instructions内部会验证时间范围，如果时间在未来会自动调整为最近24小时
        # 支持迭代查询：如果存在之前的查询结果，可以从中提取特征信息并更新查询条件
        previous_results = None
        try:
            from mcp_handler import load_mcp_results
            previous_results = load_mcp_results(args.project_path, ticket_id)
            if previous_results:
                print("  🔄 检测到之前的查询结果，将基于特征信息生成更精确的查询", file=sys.stderr)
        except Exception:
            pass  # 如果没有之前的查询结果，继续使用基础查询
        
        instructions_file = generate_mcp_instructions(
            ticket_context,
            args.project_path,
            ticket_id,
            previous_results=previous_results
        )
        
        if instructions_file:
            print(f"  ✅ MCP调用指令已生成: {instructions_file}")
            
            # 检查是否已有MCP结果
            from mcp_handler import load_mcp_results
            mcp_results = load_mcp_results(args.project_path, ticket_id)
            
            if mcp_results:
                print("  ✅ 检测到已有MCP查询结果，将直接进入阶段2")
            else:
                print("\n" + "="*60)
                print("⏳ 等待AI执行MCP查询...")
                print("="*60)
                print("\n请执行以下操作：")
                print("1. 读取MCP指令文件:", instructions_file)
                print("2. 根据指令调用SigNoz MCP工具")
                print("3. 将查询结果保存到:", instructions_file.parent / "mcp_results.json")
                print("\n完成后，运行以下命令继续分析：")
                print(f"  python {Path(__file__).name} --ticket-id {ticket_id} --project-path {args.project_path} --skip-phase0 --skip-phase1")
                
                # 如果跳过阶段2，在这里退出
                if args.skip_phase2:
                    print("\n✅ 阶段1完成，MCP指令已生成")
                    return
        else:
            print("  ⚠️  MCP调用指令生成失败")
            sys.exit(1)
    else:
        print("\n⏭️  跳过阶段1（准备与指令生成）")
        # 需要加载已有的工单上下文
        from utils import get_ticket_dir, load_json_file
        ticket_dir = get_ticket_dir(args.project_path, ticket_id)
        context_file = ticket_dir / 'ticket_context.json'
        ticket_context = load_json_file(context_file)
        if not ticket_context:
            print(f"❌ 无法加载工单上下文: {context_file}", file=sys.stderr)
            sys.exit(1)
    
    # 阶段2：综合分析
    if not args.skip_phase2:
        analysis_result = init_phase_2(
            args.project_path,
            ticket_id,
            ticket_context
        )
        
        if analysis_result:
            print("\n✅ 工单分析完成！")
            if analysis_result.get('solution_file'):
                print(f"   解决方案文档: {analysis_result['solution_file']}")
            if analysis_result.get('experience_file'):
                print(f"   经验文件: {analysis_result['experience_file']}")
        else:
            print("\n⚠️  工单分析未完成")
    else:
        print("\n⏭️  跳过阶段2（综合分析）")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}", file=sys.stderr)
        if '--verbose' in sys.argv or '-v' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)
