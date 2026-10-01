import { useState } from 'react';

const MAX_LENGTH = 255;

export function TodoForm({ onSubmit }) {
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const value = description.trim();
    if (!value) return;

    setSubmitting(true);
    try {
      await onSubmit(value);
      setDescription('');
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="todo">ToDo: </label>
        <input
          id="todo"
          type="text"
          value={description}
          maxLength={MAX_LENGTH}
          onChange={(event) => setDescription(event.target.value)}
          required
        />
      </div>
      <div style={{ marginTop: '5px' }}>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Adding...' : 'Add ToDo!'}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
