import React, { useEffect, useRef, useState } from 'react';
import { Card, Button, Space, message, Modal, Input, Select } from 'antd';
import { SaveOutlined, EyeOutlined, UndoOutlined, RedoOutlined, MobileOutlined, TabletOutlined, DesktopOutlined } from '@ant-design/icons';
import grapesjs, { Editor } from 'grapesjs';
import 'grapesjs/dist/css/grapes.min.css';
import webpage from 'grapesjs-preset-webpage';
import styled from 'styled-components';

const EditorContainer = styled.div`
  height: calc(100vh - 200px);
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
`;

const ToolbarContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
`;

interface SaveModalProps {
  visible: boolean;
  onCancel: () => void;
  onSave: (name: string, type: string) => void;
}

const SaveModal: React.FC<SaveModalProps> = ({ visible, onCancel, onSave }) => {
  const [name, setName] = useState('');
  const [type, setType] = useState('dashboard');

  const handleSave = () => {
    if (!name.trim()) {
      message.error('Lütfen sayfa adı girin');
      return;
    }
    onSave(name, type);
    setName('');
    onCancel();
  };

  return (
    <Modal
      title="Sayfayı Kaydet"
      open={visible}
      onCancel={onCancel}
      onOk={handleSave}
      okText="Kaydet"
      cancelText="İptal"
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <label>Sayfa Adı:</label>
          <Input 
            value={name} 
            onChange={(e) => setName(e.target.value)}
            placeholder="Örn: Ana Dashboard, Sipariş Listesi"
            style={{ marginTop: 4 }}
          />
        </div>
        <div>
          <label>Sayfa Tipi:</label>
          <Select
            value={type}
            onChange={setType}
            style={{ width: '100%', marginTop: 4 }}
            options={[
              { value: 'dashboard', label: 'Dashboard' },
              { value: 'list', label: 'Liste Sayfası' },
              { value: 'form', label: 'Form Sayfası' },
              { value: 'report', label: 'Rapor Sayfası' },
              { value: 'custom', label: 'Özel Sayfa' },
            ]}
          />
        </div>
      </Space>
    </Modal>
  );
};

const VisualEditor: React.FC = () => {
  const editorRef = useRef<HTMLDivElement>(null);
  const [editor, setEditor] = useState<Editor | null>(null);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [currentDevice, setCurrentDevice] = useState('desktop');

  useEffect(() => {
    if (!editorRef.current) return;

    const editorInstance = grapesjs.init({
      container: editorRef.current,
      plugins: [webpage],
      pluginsOpts: {
        [webpage as string]: {
          blocks: ['link-block', 'quote', 'text-basic'],
        }
      },
      blockManager: {
        appendTo: '#blocks',
        blocks: [
          {
            id: 'section',
            label: 'Bölüm',
            attributes: { class: 'gjs-block-section' },
            content: '<section class="section"><div class="container"><h2>Başlık</h2><p>İçerik buraya gelecek</p></div></section>',
          },
          {
            id: 'text',
            label: 'Metin',
            content: '<div class="text-component">Metin buraya yazın</div>',
          },
          {
            id: 'image',
            label: 'Resim',
            content: '<img src="https://via.placeholder.com/300x200" alt="Resim"/>',
          },
          {
            id: 'card',
            label: 'Kart',
            content: `
              <div class="card" style="border: 1px solid #d9d9d9; border-radius: 8px; padding: 24px; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                <h3>Kart Başlığı</h3>
                <p>Kart içeriği buraya gelecek</p>
                <button style="background: #1890ff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">Buton</button>
              </div>
            `,
          },
          {
            id: 'table',
            label: 'Tablo',
            content: `
              <table style="width: 100%; border-collapse: collapse; border: 1px solid #d9d9d9;">
                <thead style="background: #fafafa;">
                  <tr>
                    <th style="border: 1px solid #d9d9d9; padding: 12px; text-align: left;">Başlık 1</th>
                    <th style="border: 1px solid #d9d9d9; padding: 12px; text-align: left;">Başlık 2</th>
                    <th style="border: 1px solid #d9d9d9; padding: 12px; text-align: left;">Başlık 3</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="border: 1px solid #d9d9d9; padding: 12px;">Veri 1</td>
                    <td style="border: 1px solid #d9d9d9; padding: 12px;">Veri 2</td>
                    <td style="border: 1px solid #d9d9d9; padding: 12px;">Veri 3</td>
                  </tr>
                </tbody>
              </table>
            `,
          },
          {
            id: 'chart-placeholder',
            label: 'Grafik',
            content: `
              <div class="chart-placeholder" style="border: 2px dashed #d9d9d9; padding: 40px; text-align: center; background: #fafafa; border-radius: 8px;">
                <p style="color: #999; margin: 0;">📊 Grafik Bölgesi</p>
                <small style="color: #666;">Buraya dinamik grafik gelecek</small>
              </div>
            `,
          },
        ],
      },
      storageManager: {
        id: 'gjs-',
        type: 'local',
        autosave: true,
        autoload: true,
      },
      deviceManager: {
        devices: [
          {
            name: 'Desktop',
            width: '',
          },
          {
            name: 'Tablet',
            width: '768px',
            widthMedia: '992px',
          },
          {
            name: 'Mobile',
            width: '320px',
            widthMedia: '768px',
          },
        ],
      },
      panels: {
        defaults: [
          {
            id: 'layers',
            el: '#layers',
            resizable: {
              maxDim: 350,
              minDim: 200,
              tc: false,
              cl: true,
              cr: false,
              bc: false,
              keyWidth: 'flex-basis',
            },
          },
          {
            id: 'styles',
            el: '#styles',
            resizable: {
              maxDim: 350,
              minDim: 200,
              tc: false,
              cl: true,
              cr: false,
              bc: false,
              keyWidth: 'flex-basis',
            },
          },
          {
            id: 'traits',
            el: '#traits',
            resizable: {
              maxDim: 350,
              minDim: 200,
              tc: false,
              cl: true,
              cr: false,
              bc: false,
              keyWidth: 'flex-basis',
            },
          },
        ],
      },
      canvas: {
        styles: [
          'https://cdn.jsdelivr.net/npm/antd@5.27.1/dist/reset.css',
        ],
      },
    });

    setEditor(editorInstance);

    return () => {
      editorInstance.destroy();
    };
  }, []);

  const handleSave = (name: string, type: string) => {
    if (!editor) return;
    
    const html = editor.getHtml();
    const css = editor.getCss();
    
    // Burada backend'e kaydet
    console.log('Kaydedilen sayfa:', { name, type, html, css });
    
    // Local storage'a da kaydet
    localStorage.setItem(`page_${name}`, JSON.stringify({
      name,
      type,
      html,
      css,
      created: new Date().toISOString()
    }));
    
    message.success('Sayfa başarıyla kaydedildi!');
  };

  const handlePreview = () => {
    if (!editor) return;
    
    const html = editor.getHtml();
    const css = editor.getCss();
    
    const previewWindow = window.open('', '_blank');
    if (previewWindow) {
      previewWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Önizleme</title>
          <style>${css}</style>
          <link href="https://cdn.jsdelivr.net/npm/antd@5.27.1/dist/reset.css" rel="stylesheet">
        </head>
        <body>${html}</body>
        </html>
      `);
      previewWindow.document.close();
    }
  };

  const handleDeviceChange = (device: string) => {
    if (!editor) return;
    
    setCurrentDevice(device);
    const deviceManager = editor.DeviceManager;
    deviceManager.select(device === 'desktop' ? 'Desktop' : device === 'tablet' ? 'Tablet' : 'Mobile');
  };

  const handleUndo = () => {
    if (editor) editor.UndoManager.undo();
  };

  const handleRedo = () => {
    if (editor) editor.UndoManager.redo();
  };

  return (
    <div>
      <ToolbarContainer>
        <Space>
          <Button icon={<UndoOutlined />} onClick={handleUndo}>
            Geri Al
          </Button>
          <Button icon={<RedoOutlined />} onClick={handleRedo}>
            İleri Al
          </Button>
        </Space>
        
        <Space>
          <Button 
            type={currentDevice === 'desktop' ? 'primary' : 'default'}
            icon={<DesktopOutlined />}
            onClick={() => handleDeviceChange('desktop')}
          >
            Masaüstü
          </Button>
          <Button 
            type={currentDevice === 'tablet' ? 'primary' : 'default'}
            icon={<TabletOutlined />}
            onClick={() => handleDeviceChange('tablet')}
          >
            Tablet
          </Button>
          <Button 
            type={currentDevice === 'mobile' ? 'primary' : 'default'}
            icon={<MobileOutlined />}
            onClick={() => handleDeviceChange('mobile')}
          >
            Mobil
          </Button>
        </Space>

        <Space>
          <Button icon={<EyeOutlined />} onClick={handlePreview}>
            Önizleme
          </Button>
          <Button 
            type="primary" 
            icon={<SaveOutlined />} 
            onClick={() => setSaveModalVisible(true)}
          >
            Kaydet
          </Button>
        </Space>
      </ToolbarContainer>

      <div style={{ display: 'flex', height: 'calc(100vh - 200px)', gap: '16px' }}>
        {/* Sol Panel - Bloklar ve Katmanlar */}
        <Card 
          size="small" 
          style={{ width: '250px', height: '100%', overflow: 'auto' }}
          bodyStyle={{ padding: '12px' }}
        >
          <div id="blocks" style={{ marginBottom: '20px' }}></div>
          <div id="layers"></div>
        </Card>

        {/* Ana Editör */}
        <EditorContainer>
          <div ref={editorRef} style={{ height: '100%' }}></div>
        </EditorContainer>

        {/* Sağ Panel - Stiller ve Özellikler */}
        <Card 
          size="small" 
          style={{ width: '300px', height: '100%', overflow: 'auto' }}
          bodyStyle={{ padding: '12px' }}
        >
          <div id="styles" style={{ marginBottom: '20px' }}></div>
          <div id="traits"></div>
        </Card>
      </div>

      <SaveModal
        visible={saveModalVisible}
        onCancel={() => setSaveModalVisible(false)}
        onSave={handleSave}
      />
    </div>
  );
};

export default VisualEditor;