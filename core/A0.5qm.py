from A7qm_adviser import MysticAdviser


def main():
    print("✨ 欢迎来到玄机咨询室 ✨")
    adviser = MysticAdviser()

    # 显示咨询师信息
    print(f"\n咨询师: {adviser.persona['name']}")
    print(f"专长: {adviser.persona['title']}")
    print(f"擅长领域: {', '.join(adviser.persona['specialty'])}")

    while True:
        print("\n请选择服务类型：")
        print("1. 奇门遁甲")
        print("2. 八字命理分析")
        print("3. 综合")
        print("4. 退出")

        choice = input("请输入选项: ")

        if choice == '4':
            print("感谢咨询，愿铉錚下次能为你引路！")
            break

        method_map = {
            '1': '奇门遁甲',
            '2': '八字',
            '3': '综合'
        }

        method = method_map.get(choice, '奇门遁甲')

        if choice == '3':
            # 综合报告需要更多信息
            print("\n请提供以下信息生成综合报告：")
            name = input("姓名: ")
            birth_date = input("出生日期阳历（YYYY-MM-DD）: ")
            birth_time = input("出生时间（HH:MM，如不详可跳过）: ")
            question = input("当前最关心的生活领域（感情/事业/健康/寻物/选岗等等任何问题）: ")

            client_info = f"""
            ## 客户基本信息
            姓名：{name}
            出生日期：{birth_date}
            {f"出生时间：{birth_time}" if birth_time else ""}

            ## 咨询重点
            {question}
            """

            print("\n 正在连线铉錚大佬，请稍候...")
            report = adviser.generate_report(client_info)

            print("\n" + "=" * 50)
            print(" 你的东方玄学报告 ")
            print("=" * 50)
            print(report)

            # 保存报告
            save = input("\n是否保存报告？(y/n): ").lower()
            if save == 'y':
                filename = f"{name}_玄学报告_{datetime.now().strftime('%Y%m%d')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"报告已保存为 {filename}")
        else:
            # 单次咨询
            question = input("\n请输入你的问题或困惑: ")
            print("\n正在呼叫铉錚大佬，请稍候...")
            result = adviser.ask_oracle(question, method)

            print("\n" + "=" * 50)
            print(f" {method}读盘面分析结果 ")
            print("=" * 50)
            print(result)
            print("\n愿铉錚带给你光明与力量 ")


if __name__ == "__main__":
    main()