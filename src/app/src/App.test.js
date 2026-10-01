import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

const jsonResponse = (body, status = 200) =>
  Promise.resolve({ ok: status < 400, status, json: () => Promise.resolve(body) });

const mockFetch = (implementation) => {
  global.fetch = jest.fn(implementation);
};

test('renders todos from the backend', async () => {
  mockFetch(() => jsonResponse([{ id: '1', description: 'Learn Docker' }]));
  render(<App />);
  expect(await screen.findByText('Learn Docker')).toBeInTheDocument();
});

test('creates a todo and refreshes the list', async () => {
  const todos = [];
  mockFetch((url, options = {}) => {
    if (options.method === 'POST') {
      const todo = { id: '1', ...JSON.parse(options.body) };
      todos.push(todo);
      return jsonResponse(todo, 201);
    }
    return jsonResponse([...todos]);
  });
  render(<App />);
  expect(await screen.findByText('No TODOs yet.')).toBeInTheDocument();

  userEvent.type(screen.getByLabelText(/todo/i), '  Learn React  ');
  userEvent.click(screen.getByRole('button', { name: /add todo/i }));

  expect(await screen.findByText('Learn React')).toBeInTheDocument();
  expect(screen.getByLabelText(/todo/i)).toHaveValue('');
});

test('shows the backend error when creating fails', async () => {
  mockFetch((url, options = {}) =>
    options.method === 'POST' ? jsonResponse({ error: 'description is required' }, 400) : jsonResponse([]));
  render(<App />);
  await screen.findByText('No TODOs yet.');

  userEvent.type(screen.getByLabelText(/todo/i), 'x');
  userEvent.click(screen.getByRole('button', { name: /add todo/i }));

  expect(await screen.findByText('description is required')).toBeInTheDocument();
});
