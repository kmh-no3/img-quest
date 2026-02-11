export interface HelpContent {
  title: string;
  content: string;
  tips?: string[];
}

export const helpContent: Record<string, HelpContent> = {
  'project-list': {
    title: 'プロジェクト一覧',
    content: `
      <p class="mb-3">作成したプロジェクトの一覧です。各プロジェクトには以下の情報が表示されます：</p>
      <ul class="list-disc list-inside space-y-1 mb-3">
        <li><strong>プロジェクト名:</strong> 作成時に設定した名前</li>
        <li><strong>モード:</strong> 初心者モード（5問）or 玄人モード（8問）</li>
        <li><strong>進捗:</strong> 回答済み質問数 / 全質問数</li>
        <li><strong>ステータス:</strong> 対応可能、前の設定が未完了、完了の件数</li>
      </ul>
      <p>「新規プロジェクト作成」ボタンで新しいプロジェクトを開始できます。</p>
    `,
    tips: [
      'プロジェクトをクリックすると詳細画面に移動します',
      '複数のプロジェクトを並行して管理できます',
    ],
  },
  'project-create': {
    title: 'プロジェクト作成',
    content: `
      <p class="mb-3">新しいFI導入プロジェクトを作成します。</p>
      <div class="mb-3">
        <p class="font-semibold mb-2">必須入力項目：</p>
        <ul class="list-disc list-inside space-y-1">
          <li><strong>プロジェクト名:</strong> 任意の名前（例: 〇〇社FI導入）</li>
          <li><strong>モード:</strong> 初心者モード（5問、推奨値あり）か玄人モード（8問、全設定）を選択</li>
        </ul>
      </div>
      <div class="mb-3">
        <p class="font-semibold mb-2">オプション項目：</p>
        <ul class="list-disc list-inside space-y-1">
          <li><strong>国:</strong> 税制や法規制に影響（例: JP）</li>
          <li><strong>通貨:</strong> 基準通貨（例: JPY）</li>
          <li><strong>業種:</strong> 業界特有の要件を考慮</li>
          <li><strong>会社数:</strong> 連結対象の会社数</li>
        </ul>
      </div>
    `,
    tips: [
      'SAPが初めての方は「初心者モード」がおすすめです',
      '後からモードは変更できないので慎重に選択してください',
    ],
  },
  'project-detail': {
    title: 'プロジェクト詳細',
    content: `
      <p class="mb-3">プロジェクトの概要と、各機能へのアクセスポイントです。</p>
      <div class="mb-3">
        <p class="font-semibold mb-2">主要機能：</p>
        <ul class="list-disc list-inside space-y-1">
          <li><strong>ウィザード:</strong> 質問に答えて設定を決定します</li>
          <li><strong>バックログ:</strong> 設定項目の一覧と依存関係を確認します</li>
          <li><strong>成果物:</strong> 決定事項や設定一覧をダウンロードします</li>
        </ul>
      </div>
      <p>進捗状況のグラフで、現在の進行度を確認できます。</p>
    `,
    tips: [
      'まずは「ウィザード」から始めましょう',
      '全て回答済みになったら「成果物」を生成できます',
    ],
  },
  'wizard': {
    title: 'ウィザード',
    content: `
      <p class="mb-3">質問に順番に答えていく画面です。依存関係を考慮して、答えられる質問だけが表示されます。</p>
      <div class="mb-3">
        <p class="font-semibold mb-2">使い方：</p>
        <ul class="list-disc list-inside space-y-1">
          <li>各質問に選択肢やテキストで回答します</li>
          <li>必須項目には赤い * マークがあります</li>
          <li>初心者モードでは「推奨値を使用」ボタンで推奨設定を入力できます</li>
          <li>「前の質問」ボタンで直前の質問に戻れます</li>
          <li>「次へ」で回答を保存して次の質問に進みます</li>
        </ul>
      </div>
      <p class="mb-3">画面上部の進捗バーで、全体の何％まで完了したかわかります。</p>
      <p>「後で」ボタンで一時中断し、後から続きを回答できます。</p>
    `,
    tips: [
      '推奨値は多くの日本企業で使われている設定です',
      '回答はバックログから後で修正できます',
      '編集モード（?edit=XX）では既存の回答が表示されます',
    ],
  },
  'backlog': {
    title: 'バックログ',
    content: `
      <p class="mb-3">全ての設定項目と、それぞれのステータスを一覧表示します。</p>
      <div class="mb-3">
        <p class="font-semibold mb-2">ステータスの意味：</p>
        <ul class="list-disc list-inside space-y-1">
          <li><strong>✅ 完了:</strong> 回答済み。「編集」ボタンで再編集可能</li>
          <li><strong>🟢 対応可能:</strong> 今すぐ回答できる項目</li>
          <li><strong>🔴 前の設定が未完了:</strong> 他の項目に依存しており、まだ回答できない</li>
          <li><strong>⚪ 保留:</strong> 初期状態</li>
        </ul>
      </div>
      <p class="mb-3">「依存関係」列で、各項目が依存している設定を確認できます。</p>
      <p>フィルタボタンで、特定のステータスの項目だけを表示できます。</p>
    `,
    tips: [
      '「前の設定が未完了」の項目は、依存先を先に回答してください',
      '「対応可能」が0件になったら、全て回答済みです',
      '編集ボタンから回答を変更できます',
    ],
  },
  'artifacts': {
    title: '成果物',
    content: `
      <p class="mb-3">全ての質問に回答すると、以下の成果物をMarkdown形式で生成できます：</p>
      <div class="mb-3">
        <ul class="list-disc list-inside space-y-1">
          <li><strong>Decision Log:</strong> 意思決定の記録</li>
          <li><strong>Config Workbook:</strong> 必要な設定項目の一覧</li>
          <li><strong>Test View:</strong> テスト観点の一覧</li>
          <li><strong>Migration View:</strong> 移行対象のオブジェクト一覧</li>
        </ul>
      </div>
      <p class="mb-3">「生成」ボタンをクリックすると、回答内容を元に成果物が作成されます。</p>
      <p>各成果物の「ダウンロード」ボタンで.mdファイルとして保存できます。</p>
    `,
    tips: [
      '未回答の項目がある場合、TBD（未確定）として記載されます',
      '成果物は何度でも再生成できます',
      'Markdownファイルは汎用的なテキストエディタで開けます',
    ],
  },
};
