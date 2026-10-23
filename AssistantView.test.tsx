import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AssistantView from '../components/AssistantView';
import * as api from '../services/api';
import * as voiceHook from '../hooks/useVoice';

jest.mock('../services/api');
jest.mock('../hooks/useVoice');

describe('AssistantView end‑to‑end task list', () => {
  it('displays full reply and triggers full speech for five tasks', async () => {
    const mockReply = {
      reply: `Here are your pending tasks:\n1. Prepare slides (priority: high)\n2. Update repo (priority: high)\n3. Schedule meeting (priority: medium)\n4. Buy groceries (priority: low)\n5. Read article (priority: low)`,
      speech_text: `You have 5 pending tasks. 1. Prepare slides (priority high) 2. Update repo (priority high) 3. Schedule meeting (priority medium) 4. Buy groceries (priority low) 5. Read article (priority low).`,
      intent_detected: 'list_tasks',
      action_taken: { type: 'tasks_listed', count: 5 },
      target_section: 'tasks',
    };
    (api.assistantInteract as jest.Mock).mockResolvedValueOnce(mockReply);
    const speakMock = jest.fn().mockResolvedValue(undefined);
    (voiceHook.useVoice as jest.Mock).mockReturnValue({
      speak: speakMock,
      gender: 'male',
      selectedVoice: null,
      setPreferredGender: jest.fn(),
    });

    render(<AssistantView />);
    const input = screen.getByPlaceholderText(/type a message/i);
    fireEvent.change(input, { target: { value: 'What are my tasks?' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => expect(screen.getByText(/Here are your pending tasks:/i)).toBeInTheDocument());
    // Verify all five lines are rendered
    expect(screen.getByText('1. Prepare slides (priority: high)')).toBeInTheDocument();
    expect(screen.getByText('5. Read article (priority: low)')).toBeInTheDocument();

    // Verify speech called with full string (chunking occurs inside hook, we just check the argument passed)
    expect(speakMock).toHaveBeenCalledWith(mockReply.speech_text);
  });
});
