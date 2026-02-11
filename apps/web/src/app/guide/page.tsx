'use client';

import { useRouter } from 'next/navigation';

export default function GuidePage() {
  const router = useRouter();

  return (
    <div className="max-w-5xl mx-auto">
      {/* ヘッダー */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">IMG-Quest 使い方ガイド</h1>
        <p className="text-lg text-gray-600">
          SAP FI導入の意思決定を疑似体験し、設定項目と成果物を自動生成するアプリケーションです
        </p>
      </div>

      {/* 目次 */}
      <div className="card mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">目次</h2>
        <nav className="space-y-2">
          <a href="#quickstart" className="block text-primary-600 hover:text-primary-700 hover:underline">
            1. クイックスタート（5分で理解）
          </a>
          <a href="#detailed" className="block text-primary-600 hover:text-primary-700 hover:underline">
            2. 詳細ガイド
          </a>
          <a href="#glossary" className="block text-primary-600 hover:text-primary-700 hover:underline">
            3. SAP用語集
          </a>
        </nav>
      </div>

      {/* セクション1: クイックスタート */}
      <section id="quickstart" className="mb-12">
        <div className="card">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">1. クイックスタート</h2>
          
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">IMG-Questとは？</h3>
              <p className="text-gray-700 leading-relaxed">
                IMG-Questは、SAP FI（財務会計）導入時に必要な設定項目を、質問に答えるだけで洗い出せるツールです。
                依存関係を自動管理し、決定事項や設定一覧などの成果物を生成します。
              </p>
              <div className="mt-3 p-4 bg-blue-50 border-l-4 border-blue-500">
                <p className="text-sm text-blue-900">
                  <strong>対象者:</strong> FIコンサル育成、FI領域リード、顧客キーマンの論点可視化
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">基本的な使い方（3ステップ）</h3>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                    1
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">プロジェクトを作成</h4>
                    <p className="text-gray-700">
                      会社の基本情報（国、通貨、業種など）を入力し、初心者モードか玄人モードを選択します。
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                    2
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">ウィザードで回答</h4>
                    <p className="text-gray-700">
                      質問に順番に答えていきます。初心者モードなら5問、玄人モードなら8問です。
                      回答はバックログから後で修正できます。
                    </p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg">
                    3
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1">成果物を生成</h4>
                    <p className="text-gray-700">
                      全ての質問に回答したら、決定事項や設定一覧などの成果物をMarkdown形式でダウンロードできます。
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-3">モードの違い</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 border-2 border-green-200 bg-green-50 rounded-lg">
                  <h4 className="font-bold text-green-900 mb-2">カンタン設定ver（初心者モード）</h4>
                  <ul className="text-sm text-green-800 space-y-1">
                    <li>• 質問数: 5問</li>
                    <li>• 専門用語を噛み砕いた説明</li>
                    <li>• 推奨値が提示される</li>
                    <li>• SAPが初めての方向け</li>
                  </ul>
                </div>
                <div className="p-4 border-2 border-purple-200 bg-purple-50 rounded-lg">
                  <h4 className="font-bold text-purple-900 mb-2">完全マニュアルver（玄人モード）</h4>
                  <ul className="text-sm text-purple-800 space-y-1">
                    <li>• 質問数: 8問</li>
                    <li>• 詳細な設定項目まで網羅</li>
                    <li>• 全パラメータを細かく設定可能</li>
                    <li>• SAPの知見がある方向け</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">アプリケーションの流れ</h3>
              <div className="bg-white p-4 rounded border border-gray-300">
                <pre className="text-sm text-gray-700 overflow-x-auto">
{`アプリ起動
    ↓
プロジェクト一覧
    ↓
新規プロジェクト作成
    ↓
モード選択（初心者 or 玄人）
    ↓
ウィザードで回答
    ↓
（必要に応じて）バックログから編集
    ↓
全て回答済み？
    ↓
成果物生成・ダウンロード`}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* セクション2: 詳細ガイド */}
      <section id="detailed" className="mb-12">
        <div className="card">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">2. 詳細ガイド</h2>
          
          <div className="space-y-8">
            {/* プロジェクト作成 */}
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-b-2 border-primary-200 pb-2">
                2.1 プロジェクト作成
              </h3>
              <div className="space-y-4">
                <p className="text-gray-700">
                  プロジェクト作成画面では、以下の情報を入力します：
                </p>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-300">
                        <th className="text-left py-2 pr-4 font-semibold text-gray-900">項目</th>
                        <th className="text-left py-2 font-semibold text-gray-900">説明</th>
                      </tr>
                    </thead>
                    <tbody className="text-gray-700">
                      <tr className="border-b border-gray-200">
                        <td className="py-2 pr-4">プロジェクト名</td>
                        <td className="py-2">任意の名前（例: 〇〇社FI導入）</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="py-2 pr-4">モード</td>
                        <td className="py-2">初心者モード or 玄人モード</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="py-2 pr-4">国</td>
                        <td className="py-2">税制や法規制に影響（例: JP、US）</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="py-2 pr-4">通貨</td>
                        <td className="py-2">基準通貨（例: JPY、USD）</td>
                      </tr>
                      <tr className="border-b border-gray-200">
                        <td className="py-2 pr-4">業種</td>
                        <td className="py-2">業界特有の要件を考慮</td>
                      </tr>
                      <tr>
                        <td className="py-2 pr-4">会社数</td>
                        <td className="py-2">連結対象の会社数</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* ウィザード画面 */}
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-b-2 border-primary-200 pb-2">
                2.2 ウィザード画面
              </h3>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">質問への回答方法</h4>
                  <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
                    <li>各質問には選択肢、テキスト入力、数値入力などの形式があります</li>
                    <li>必須項目には赤い * マークが表示されます</li>
                    <li>初心者モードでは、推奨値が提示されます</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">推奨値の使い方</h4>
                  <p className="text-gray-700 mb-2">
                    初心者モードでは、各入力項目の右上に「推奨値を使用」ボタンが表示されます。
                    クリックすると、日本企業で一般的な設定値が自動入力されます。
                  </p>
                  <div className="bg-green-50 border-l-4 border-green-500 p-3">
                    <p className="text-sm text-green-900">
                      💡 推奨値は多くの日本企業で採用されている設定ですが、自社の要件に合わせて変更できます。
                    </p>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">「前の質問に戻る」機能</h4>
                  <p className="text-gray-700">
                    ウィザード進行中、画面下部の「前の質問」ボタンで直前の質問に戻れます。
                    回答は保存されているので、確認や修正が可能です。
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">進捗の見方</h4>
                  <p className="text-gray-700">
                    画面上部に「質問 X / Y」と進捗バーが表示されます。
                    初心者モードはY=5、玄人モードはY=8です。
                  </p>
                </div>
              </div>
            </div>

            {/* バックログ画面 */}
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-b-2 border-primary-200 pb-2">
                2.3 バックログ画面
              </h3>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">ステータスの意味</h4>
                  <div className="space-y-2">
                    <div className="flex items-start gap-3">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                        ✅ 完了
                      </span>
                      <p className="text-gray-700 text-sm flex-1 mt-1">
                        回答済みの項目です。「編集」ボタンから再編集できます。
                      </p>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
                        🟢 対応可能
                      </span>
                      <p className="text-gray-700 text-sm flex-1 mt-1">
                        依存関係が解決済みで、今すぐ回答できる項目です。
                      </p>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
                        🔴 前の設定が未完了
                      </span>
                      <p className="text-gray-700 text-sm flex-1 mt-1">
                        他の項目に依存しており、まだ回答できません。依存先を先に回答してください。
                      </p>
                    </div>
                    <div className="flex items-start gap-3">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                        ⚪ 保留
                      </span>
                      <p className="text-gray-700 text-sm flex-1 mt-1">
                        初期状態の項目です。
                      </p>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">依存関係の理解</h4>
                  <p className="text-gray-700 mb-2">
                    設定項目には依存関係があります。例えば、「会計年度」を先に決めないと「期間」の設定ができません。
                  </p>
                  <div className="bg-yellow-50 border-l-4 border-yellow-500 p-3">
                    <p className="text-sm text-yellow-900">
                      ⚠️ 「前の設定が未完了」項目は、依存関係の列を見て、どの項目を先に回答すべきか確認できます。
                    </p>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">回答の編集方法</h4>
                  <p className="text-gray-700">
                    完了済みの項目には「編集」ボタンが表示されます。クリックするとウィザード画面が開き、
                    既存の回答が入力された状態で修正できます。更新後は自動的にバックログに戻ります。
                  </p>
                </div>
              </div>
            </div>

            {/* 成果物生成 */}
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-b-2 border-primary-200 pb-2">
                2.4 成果物生成
              </h3>
              <div className="space-y-4">
                <p className="text-gray-700">
                  全ての質問に回答すると、以下の成果物をMarkdown形式で生成できます：
                </p>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-bold text-blue-900 mb-2">Decision Log</h4>
                    <p className="text-sm text-blue-800">
                      意思決定の記録。どの質問にどう答えたか、その根拠が記載されます。
                    </p>
                  </div>
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <h4 className="font-bold text-green-900 mb-2">Config Workbook</h4>
                    <p className="text-sm text-green-800">
                      必要な設定項目の一覧。SAP設定時の作業リストとして使用できます。
                    </p>
                  </div>
                  <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                    <h4 className="font-bold text-purple-900 mb-2">Test View</h4>
                    <p className="text-sm text-purple-800">
                      テスト観点の一覧。最低限確認すべきテストケースが記載されます。
                    </p>
                  </div>
                  <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                    <h4 className="font-bold text-orange-900 mb-2">Migration View</h4>
                    <p className="text-sm text-orange-800">
                      移行対象のオブジェクト一覧。データ移行計画に活用できます。
                    </p>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">ダウンロード方法</h4>
                  <p className="text-gray-700">
                    成果物画面で「生成」ボタンをクリックすると、各成果物が生成されます。
                    成果物ごとに「ダウンロード」ボタンが表示され、Markdown（.md）ファイルとして保存できます。
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* セクション3: SAP用語集 */}
      <section id="glossary" className="mb-12">
        <div className="card">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">3. SAP用語集</h2>
          <p className="text-gray-700 mb-6">
            IMG-Questで扱う主要なSAP FI用語の解説です。
          </p>
          
          <div className="space-y-4">
            <div className="border-l-4 border-primary-500 pl-4 py-2">
              <h4 className="font-bold text-gray-900 mb-1">会計年度バリアント (Fiscal Year Variant)</h4>
              <p className="text-gray-700 text-sm mb-1">
                会計年度と会計期間の定義。日本企業の多くは4月始まり（3月決算）のK4を使用します。
              </p>
              <p className="text-xs text-gray-600">
                <strong>IMG-Quest内:</strong> 最初に決定する重要項目。期間管理に影響します。
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4 py-2">
              <h4 className="font-bold text-gray-900 mb-1">会社コード (Company Code)</h4>
              <p className="text-gray-700 text-sm mb-1">
                法人格を持つ独立した会計単位。財務諸表を作成する最小単位です。
              </p>
              <p className="text-xs text-gray-600">
                <strong>IMG-Quest内:</strong> プロジェクト作成時の「会社数」に関連します。
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4 py-2">
              <h4 className="font-bold text-gray-900 mb-1">統制勘定 (Reconciliation Account)</h4>
              <p className="text-gray-700 text-sm mb-1">
                債権債務の補助元帳（得意先元帳・仕入先元帳）と総勘定元帳を紐付ける勘定科目。
              </p>
              <p className="text-xs text-gray-600">
                <strong>IMG-Quest内:</strong> AP/AR設定で選択します。
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4 py-2">
              <h4 className="font-bold text-gray-900 mb-1">オープンアイテム管理 (Open Item Management)</h4>
              <p className="text-gray-700 text-sm mb-1">
                未消込の取引（未入金・未払い）を明細レベルで管理する機能。
              </p>
              <p className="text-xs text-gray-600">
                <strong>IMG-Quest内:</strong> 勘定科目設定で選択します。
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4 py-2">
              <h4 className="font-bold text-gray-900 mb-1">消込 (Clearing)</h4>
              <p className="text-gray-700 text-sm mb-1">
                請求と入金、発注と支払いなど、対となる取引を紐付けて残高をゼロにする処理。
              </p>
              <p className="text-xs text-gray-600">
                <strong>IMG-Quest内:</strong> 消込単位の質問で設定します。
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4 py-2">
              <h4 className="font-bold text-gray-900 mb-1">支払条件 (Payment Terms)</h4>
              <p className="text-gray-700 text-sm mb-1">
                支払期日や割引条件を定義するマスタ（例: 末締め翌月末払い）。
              </p>
              <p className="text-xs text-gray-600">
                <strong>IMG-Quest内:</strong> AP/AR設定で定義します。
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4 py-2">
              <h4 className="font-bold text-gray-900 mb-1">転記キー (Posting Key)</h4>
              <p className="text-gray-700 text-sm mb-1">
                仕訳の借方・貸方や勘定科目タイプを制御するコード（例: 50=総勘定元帳借方）。
              </p>
              <p className="text-xs text-gray-600">
                <strong>IMG-Quest内:</strong> 伝票タイプ設定で使用されます。
              </p>
            </div>

            <div className="border-l-4 border-primary-500 pl-4 py-2">
              <h4 className="font-bold text-gray-900 mb-1">勘定グループ (Account Group)</h4>
              <p className="text-gray-700 text-sm mb-1">
                勘定科目や取引先マスタを分類し、採番ルールや入力項目を制御するグループ。
              </p>
              <p className="text-xs text-gray-600">
                <strong>IMG-Quest内:</strong> マスタ設定方針で選択します。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* フッターアクション */}
      <div className="flex gap-4 justify-center mb-8">
        <button
          onClick={() => router.push('/')}
          className="btn btn-secondary"
        >
          ← プロジェクト一覧に戻る
        </button>
        <button
          onClick={() => router.push('/projects/new')}
          className="btn btn-primary"
        >
          プロジェクトを作成する
        </button>
      </div>
    </div>
  );
}
